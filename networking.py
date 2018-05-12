import asyncio
import json
import logging
import re

import aiohttp
from colorama import Fore, Style
from unidecode import unidecode

import question


async def fetch(url, session, timeout):
    try:
        async with session.get(url, timeout=timeout) as response:
            return await response.text()
    except Exception:
        print(f"Server timeout/error to {url}")
        logging.exception(f"Server timeout/error to {url}")
        return ""


async def get_responses(urls, timeout, headers):
    tasks = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session, timeout))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses


async def get_response(url, timeout, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        return await fetch(url, session, timeout)


async def get_json_response(url, timeout, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.json()


async def websocket_handler(uri, headers):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(uri, headers=headers, heartbeat=5, timeout=30) as ws:
            print("Connected")
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    message = msg.data
                    message = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", message)

                    message_data = json.loads(message)
                    logging.info(str(message_data).encode("utf-8"))

                    if "error" in message_data and message_data["error"] == "Auth not valid":
                        logging.info(message_data)
                        raise RuntimeError("Connection settings invalid")
                    elif message_data["type"] != "interaction":
                        logging.info(message_data)
                        if message_data["type"] == "question":
                            question_str = unidecode(message_data["question"])
                            answers = [unidecode(ans["text"]) for ans in message_data["answers"]]
                            print("\n" * 5)
                            print("Question detected.")
                            print(f"Question {message_data['questionNumber']} out of {message_data['questionCount']}")
                            print(f"{Fore.CYAN}{question_str}\n{answers}{Style.RESET_ALL}")
                            print()
                            question.answer_question(question_str, answers)

    print("Socket closed")

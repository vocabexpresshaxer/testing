import re, sys, time, itertools
import urllib.request as urllib2
from google import google
from collections import defaultdict
from colorama import Fore, Style
from bs4 import BeautifulSoup
punctuation_to_none = str.maketrans({key: None for key in "!\"#$%&\'()*+,-.:;<=>?@[\\]^_`{|}~�"})
punctuation_to_space = str.maketrans({key: " " for key in "!\"#$%&\'()*+,-.:;<=>?@[\\]^_`{|}~�"})


def answer_question(question, options):
    lastA = """"""
    print("Searching")
    start = time.time()
    simq, neg = simplify_ques(question)
    maxo=""
    m=1
    if neg:m=-1
    points,maxo = google_wiki(simq, options, neg)
    for point, option in zip(points, options):
        print(option + " { points: "  + str(point*m) + " }\n")
        lastA = lastA + option + " { points: "  + str(point*m) + " }\n"
    print("\n\n" + str(maxo))
    lastA = lastA + "\n\n" + str(maxo)
    end = time.time()
    t = end - start
    with open("uk.txt", "w") as uk:uk.write(lastA)
    print("Search Took %s Seconds" % str(t))
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
def simplify_ques(question):
	question = question.lower()
	neg=False
	remove_words = ["who","what","where","when","of","and","that","have","for","the","why","the","on","with","as","this","by","from","they","a","an","and","my","are","in","to","these","is","does","which","his","her","also","have","it","not","we","means","you","comes","came","come","about","if","by","from","go","?",",","!","'","has","\""]
	negative_words = ["not","isn\"t","except","don\"t","doesn\"t","wasn\"t","wouldn\"t","can\"t"]
	qwords = question.split()
	if [i for i in qwords if i in negative_words]:
		neg=True
	
	#remove neg word
	for w in qwords:
		if w in negative_words:
			qwords = qwords.remove(w)
	#i did this so fingers crossed :)
			
	cleanwords = [word for word in qwords if word.lower() not in remove_words]
	temp = ' '.join(cleanwords)
	clean_question=""
	#remove ?
	for ch in temp: 
		if ch!="?" or ch!="\"" or ch!="\'":
			clean_question=clean_question+ch
	return clean_question.lower(),neg
    
def get_page(link):
	try:
		if link.find('mailto') != -1:
			return ''
		req = urllib2.Request(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
		html = urllib2.urlopen(req).read()
		return html
	except (urllib2.URLError, urllib2.HTTPError, ValueError) as e:
		return ''

def split_string(source):
	splitlist = ",!-.;/?@ #"
	output = []
	atsplit = True
	for char in source:
		if char in splitlist:
			atsplit = True
		else:
			if atsplit:
				output.append(char)
				atsplit = False
			else:
				output[-1] = output[-1] + char
	return output

def smart_answer(content,qwords):
	zipped= zip(qwords,qwords[1:])
	points=0
	for el in zipped :
		if content.count(el[0]+" "+el[1])!=0 :
			points+=1000
	return points

def google_wiki(sim_ques, options, neg):
	num_pages = 1
	points = list()
	content = ""
	maxo=""
	maxp=-sys.maxsize
	words = split_string(sim_ques)
	for o in options:
		o = o.lower()
		original=o
		o += ' wiki'
		# get google search results for option + 'wiki'
		search_wiki = google.search(o, num_pages)
		link = search_wiki[0].link
		content = get_page(link)
		soup = BeautifulSoup(content,"lxml")
		page = soup.get_text().lower()
		temp=0
		for word in words:
			temp = temp + page.count(word)
		temp+=smart_answer(page, words)
		if neg:
			temp*=-1
		points.append(temp)
		if temp>maxp:
			maxp=temp
			maxo=original
	return points,maxo

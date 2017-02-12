import requests
from bs4 import BeautifulSoup

WON_STATUS = "won by"
jurl = "http://www.cricinfo.com/ci/engine/match/index.json"

def cricket_scr(jurl=jurl):
	r = requests.get(jurl)
	soup = BeautifulSoup(r.text,"lxml")
	matches = []
	for div in soup.select('div[class^="innings"]'):
		t = tuple(text for text in div.stripped_strings)
		matches.append(t)
	results = []
	for div in soup.select('div[class^="match-status"]'):
		t = [text for text in div.stripped_strings]
		results.append(t)
	matches_and_results = []
	single = 0
	double = 0
	while double < len(matches):
		matches_and_results.append((matches[double],matches[double+1],results[single][0]))
		single += 1
		double += 2
	return matches_and_results
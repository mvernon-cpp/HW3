'''
Crawl the CS website until the Permanent Faculty  (there  are  18  in  total)  page  is  found.  
The  target  URL  is  https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml.
'''

import re
from urllib.error import HTTPError
import urllib.parse
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient

class Frontier:
	def __init__(self, startingUrl):
		self.urls = []
		self.urls.append(startingUrl)
		self.current_index = 0
		self.end = len(self.urls)

	def done(self):
		if self.current_index == self.end:
			return True
		else:
			return False

	def nextURL(self):
		current_url = self.urls[self.current_index]
		self.current_index += 1
		return current_url

	def clear(self):
		print('clearing frontier')
		self.current_index = 0
		self.end = 0
		self.urls.clear()

	def addURL(self, url):
		#check url does not exist in list
		if url not in self.urls:
			print('adding url to frontier')
			self.urls.append(url)
			self.end += 1


def main():
	
	print('connecting to database collection pages')

	# Connecting to the database
	db = connectDataBase()

	# Creating a collection
	pages = db["pages"]    
	# storePage(pages, "urltest", "html test")

	frontier = Frontier('https://www.cpp.edu/sci/computer-science/')
	# frontier = Frontier('https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml')
	crawlerThread(frontier, pages)



def retieveHTML(url):
	print('retrieve html')

	try:
		html = urlopen( url )
	except HTTPError as e:
		return ''
	try:
		bs = BeautifulSoup(html.read(), 'html.parser')
	except AttributeError as e:
		return ''
	return bs.prettify()

def connectDataBase():
	# Creating a database connection object using pymongo

	DB_NAME = "CPPComputerScience"
	DB_HOST = "localhost"
	DB_PORT = 27017

	try:
		client = MongoClient(host=DB_HOST, port=DB_PORT)
		db = client[DB_NAME]

		return db
	except:
		print("Database not connected successfully")


def storePage(pages, url, html):
	page = {
		  "url": url,
		  "html": html,
		  "targetPage": 0
	 }
	
	pages.insert_one(page)


def targetPage(html):
	# Stop criteria 
	# <h1 class="cpp-h1">Permanent Faculty</h1>

	stop = False
	bs = BeautifulSoup(html, 'html.parser')
	all_h1 = bs.find_all('h1',{'class':'cpp-h1'} )
	for h1 in all_h1:
		stop_criteria = h1.find(string=re.compile("Permanent Faculty"))
		if stop_criteria:
			print(stop_criteria)
			stop = True
	return stop
		
def flagTargetPage(pages, url):
	page = { "$set": {
		  "targetPage": 1
	 }}
	
	pages.update_one({"url": url}, page)

def findURLS(html):
	base = 'https://www.cpp.edu/sci/computer-science/'
	urls = []
	bs = BeautifulSoup(html, 'html.parser') #html is str, cant read()
	contains_hrefs = bs.find_all(href=True)
	
	for hrefs in contains_hrefs:
		href = hrefs['href']
		# print( urllib.parse.urljoin(base, href) )
		urls.append( urllib.parse.urljoin(base, href) )
		
		sanitized_found_urls = [url for url in urls if re.search(base,url)]

	return sanitized_found_urls



def crawlerThread(frontier, pages):
	print('Starting crawler thread')

	while not frontier.done():

		url = frontier.nextURL()
		print('current url:', url)

		html = retieveHTML(url)

		# If html is '' should it be added to collection??
		# Storing it for now, no harm

		storePage(pages, url, html)

		if targetPage(html):
			print('target met, add flag, clear')
			flagTargetPage(pages, url)
			frontier.clear()
		else:
			found_urls = findURLS(html)
			# found_urls = ['https://www.cpp.edu/sci/computer-science/docs/cs_lecturers.docx','https://www.cpp.edu/sci/computer-science/']
			
			for url in found_urls:
				frontier.addURL(url)
	
	print('==========\nFinished crawler thread. Check mongoDB.\n==========')



	'''
	PSUEDOCODE (strictly follow):
	while not frontier.done() do 
		url <— frontier.nextURL() 
		html <— retrieveHTML(url) 
		storePage(url, html) 
		if target_page (html) 
			flagTargetPage(url) 
			clear_frontier() 
		else 
			for each not visited url in parse (html) do 
				frontier.addURL(url) 
			end for 
	end while
	'''

if __name__ == '__main__':
	main()
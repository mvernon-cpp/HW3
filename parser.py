'''
Read  the  CS  faculty  information,  parse  faculty  members'  name,  title,  office,  phone,  email,  and 
website, and persist this data in MongoDB - one document for each professo

Use the target page URL to find the Permanent Faculty page in the database

Requirements:  
1) Use the Python libraries BeautifulSoup and PyMongo. 
2) Use the MongoDB collection professors to persist professors' data
'''


import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient

def main():
	print('connecting to database collection pages')

	# Connecting to the database
	db = connectDataBase()

	# Creating a collection
	pages = db["pages"]    

	#query for target page
	target_page = findTargetPage(pages)

	if target_page is not None:
		html = target_page.get('html')
		print('connecting to database collection professors')
		
		# Creating a collection
		professors = db["professors"]
		parseFacultyMembers(professors, html)
	else:
		print('Target page does not exist.')


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


def findTargetPage(pages):
	return pages.find_one( {"targetPage": 1} )
	 

def parseFacultyMembers(professors, html):

	bs = BeautifulSoup(html, 'html.parser')
	
	clear_fix = bs.find_all('div', {'class':'clearfix'})

	for prof in clear_fix:
		
		p = prof.find('p')

		if p is not None:
			
			name = prof.find('h2').get_text().strip() if prof.find('h2') else "name not found"
			title = p.find(string=re.compile("Professor")).strip() if p.find(string=re.compile("Professor")) else "title not found"
			office = p.find(string=re.compile("\d-\d")).strip() if p.find(string=re.compile("\d-\d")) else "office not found"
			phone = p.find(string=re.compile("\(\d\d\d\)\s\d\d\d-\d\d\d\d")).strip() if p.find(string=re.compile("\(\d\d\d\)\s\d\d\d-\d\d\d\d")) else "phone not found"

			email = p.find(string=re.compile("[A-Za-z]*@cpp.edu")).strip() if p.find(string=re.compile("\(\d\d\d\)\s\d\d\d-\d\d\d\d")) else "email not found"

			a_ = p.find_all('a')
			website = p.find_all('a')[1].get_text().strip() if len(a_) > 1 else "website not found"

			# print('Name:', name)
			# print('Title:', title)
			# print('Office:', office)
			# print('Phone:', phone)
			# print('Email:', email)
			# print('Website:', website)

			# p_= prof.find('p').findChildren()
			# for i, child in enumerate(p_):
			# 	if i == 7:
			# 		# print(child.text)
			# 		email=child.text
			# 	if i == 10:
			# 		# print(child.text)
			# 		website=child.text
			
			storeProfessor(professors, name, title, office, phone, email, website )


def storeProfessor(professors, name, title, office, phone, email, website):
	print('='*50)
	professor = {
		  "name": name,
		  "title": title,
		  "office": office,
		  "phone": phone,
		  "email": email,
		  "website": website
	 }
	
	professors.insert_one(professor)
	print("Stored:", name, title, office, phone, email, website, sep=' | ')
	print('='*50)


if __name__ == '__main__':
	main()
#Takes each conviction and splits into different rows on the digital copies

import re, os, sys, linecache, csv

file_name = "/Users/jelias/Documents/Pardons/to_be_separated_paper.csv" #Location of the .txt file
output_file_name = "/Users/jelias/Documents/Pardons/fixed_paper.csv"
orig_file = []

# Reads input file
def read_file(file_name):
	infile = []
	with open(file_name,'r') as file:
		rowreader = csv.reader(file, delimiter=',', quotechar='"')
		for row in rowreader:
			infile.append(row)
	return infile

# Creates output file
def create_output_file(output_file,headers):
	with open(output_file,'wb') as csv_output:
		rowwriter = csv.writer(csv_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)  
		rowwriter.writerow(headers)

# Amends text to output file
def amend_file(file_name, text):
	file = open(file_name,'ab')
	rowwriter = csv.writer(file, delimiter=',')  
	rowwriter.writerow(text)
	file.close()

# Defines the headers for the output file
headers = ["is_digital","pardon_date","full_name","last_name","first_name","middle_name","title","nickname","serial_num","ef_num","gdc_num","granted","rights","offense","date_sentence_began","sentence","full","dob","race","sex","court","court1","court2","court3","court4","court5"]

# Creates the output file
create_output_file(output_file_name, headers)

orig_file = read_file(file_name)
i = 0
#Iterates through each pardon document
for l in orig_file:
	#Initializes fields
	is_digital=''
	pardon_date=''
	full_name=''
	last_name=''
	first_name=''
	middle_name=''
	title=''
	nickname=''
	serial_num=''
	ef_num=''
	gdc_num=''
	granted=''
	rights=''
	offense=''
	date_sentence_began=''
	sentence=''
	full=''
	dob=''
	race=''
	sex=''
	court=''
	court1=''
	court2=''
	court3=''
	court4=''
	court5=''

	try: 

		#Sets fields
		is_digital = 1
		pardon_date = l[1].strip()
		full_name = l[2].strip()
		serial_num=l[8].strip()
		ef_num = l[9].strip()
		gdc_num = l[10].strip()
		granted = l[11].strip()
		rights = l[12].strip()
		dob = l[17].strip()
		race = l[18].strip()
		sex = l[19].strip()
		court = l[20].strip()
		court1 = l[21].strip()
		court2 = l[22].strip()
		court3 = l[23].strip()
		court4 = l[24].strip()
		court5 = l[25].strip()
		nickname = l[7].strip()
		last_name = l[3].strip()
		first_name = l[4].strip()
		middle_name = l[5].strip()
		date_sentence_began = l[14].strip()
		full = l[16].strip()
		sentence = l[15].strip()
		title = l[6].strip()
		items = l[13].split(";")

		#Breaks each offense apart and amends each row to file
		for m in items:
			offense = m.strip()
			row = []
			for l in headers:
				row.append(eval(l))
			amend_file(output_file_name, row)
			offense = ''

		print(items)
	except Exception as e:
		print e

	i = i + 1




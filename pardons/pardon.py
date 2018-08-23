#Script to get pardon cases from .txt file

import re, os, sys, linecache, csv

orig_file = []
file_name = "" #Location of the .txt file
path_out = os.getcwd() + "\\"
output_file_name = ""
finds = {}
cases = []


# Reads input file
def read_file(file_name):
    with open(file_name,'r') as file:
        return file.read()

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

# Gets name of person
def getName(text):
	return re.findall(r'(?:WHEREAS, ?)(.*?)(?:\.? Serial)', text)

# Gets serial number of case
def getNum(text):
	return re.findall(r'(?:Serial Number ?)(.*?)(?: was)', text)

# Gets whether the pardon includes gun rights
def gunRights(text):
	matchgun = re.findall(r'(except the right)', text)
	matchgun2 = re.findall(r'(including the right)', text)
	if (matchgun == ["except the right"]):
		return False
	elif (matchgun2 == ["including the right"]):
		return True
	else:
		return None

#Gets the list of convictions, sentences and sentence dates 
def getConvictions(text):
	match = re.findall(r'(?:(?:BEGAN *_*SENTENCE)|(?:CONVICTION\s*DATE))(.*?)(?:and,)', text, re.DOTALL|re.MULTILINE)
	conviction = []
	item = {}
	for l in re.findall(r'([a-zA-Z; ]* ?)(\s+)([a-zA-Z]+ Superior)(\s*?)(\d{1,2}\S\d{1,2}\S\d{2,4})(\s+)([0-9].*?([cC]losed)|([Tt]erminated))(\s+)(.*?\d{1,2}\S\d{1,2}\S\d{2,4})', text, re.DOTALL|re.MULTILINE):
		item = {}
		item['full'] = match
		try:
			item['offense'] = l[0]
		except Exception as e: 
			item['offense'] = "Error"
		try: 
			item['court'] = l[2]
		except Exception as e:
			item['court'] = "Error"
		try:
			item['sentence1'] = l[6]
		except Exception as e:
			item['sentence1'] = "Error"
		try:
			item['sentence2'] = l[10]
		except Exception as e:
			item['sentence2'] = "Error"
		try:
			item['date'] = l[4]
		except Exception as e:
			item['date'] = "Error"
		conviction.append(item)
	return conviction


# Defines the headers for the output file
headers = ["name", "serial_num", "rights", "offense", "court", "date", "sentence", "full"]

# Creates the output file
create_output_file(output_file_name, headers)

orig_file = read_file(file_name)
i = 0
try:
	#Iterates through each pardon document
	for match in re.findall(r'(PARDON)(.*?)(FOR THE BOARD)', orig_file, re.DOTALL):
		#Initializes fields
		full_text = ""
		name = ""
		num = ""
		offense = ""
		court =""
		date = ""
		sentence = ""
		full = ""
		out = "BEGINNING ", i, match, " END"
		print("found match")
		full_text = match[1]
		name = getName(full_text)
		num = getNum(full_text)
		convictions = getConvictions(full_text)
		gun = gunRights(full_text)
		print(i, name, convictions)
		
		l=0
		row = []
		#if no convictions, amend the other parts
		if(convictions == []):
			row = [name, num, gun, offense, court, date, sentence, full]
			amend_file(output_file_name, row)
		
		#Iterate through each conviction
		for m in convictions:
			print ("conviction", l)
			print("m", m)
			offense = ""
			court =""
			date = ""
			sentence = ""

			#Split convictions into offenses, dates, court, sentence
			try: 
				offense = m['offense']
				print("Offense", offense)
			except Exception as e:
				offense = "ERROR"
			try: 
				court = m['court']
				print("court", court)
			except Exception as e:
				court = "ERROR"	
			try: 
				sentence = m['sentence1'] + m['sentence2']
			except Exception as e:
				sentence = "ERROR"	
			try: 
				full = m['full']
			except Exception as e:
				full = "ERROR"	
			try: 
				date = m['date']
			except Exception as e:
				date = "ERROR"	

			#Set row to insert to file and amend to file								
			row = [name, num, gun, offense, court, date, sentence, full]
			amend_file(output_file_name, row)
			l = l+1

		i = i+1
except Exception as e:
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(exc_type, fname, exc_tb.tb_lineno, str(e))


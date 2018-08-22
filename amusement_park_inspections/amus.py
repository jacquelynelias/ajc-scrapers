#Amusement inspections to csv
#This script uses regex to pull relevant fields from a pdf that was converted to an unstructured .txt to a .csv

import re, os, sys, linecache, csv, usaddress

orig_file = []
file_name = "" #Location of the .txt file
path_out = os.getcwd() + "\\"
output_file_name = "./amusement.csv"
finds = {}
cases = []


# Gets input text
def read_file(file_name):
    with open(file_name,'r') as file:
        return file.read()

#Creates/overwrites output file with headers
def create_output_file(output_file,headers):
	with open(output_file,'wb') as csv_output:
		rowwriter = csv.writer(csv_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)  
		rowwriter.writerow(headers)

#Amends rows to output file
def amend_file(file_name, text):
	file = open(file_name,'ab')
	rowwriter = csv.writer(file, delimiter=',')  
	rowwriter.writerow(text)
	file.close()

#Gets phone number of company
def getPhone(text):
	try:
		result = re.findall(r'(?:PHONE:\s)(\(\d{3}\) \d{3}-\d{4})', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"	

#Gets phone number of contact
def getContactPhone(text):
	try:
		result = re.findall(r'(?:PERMIT CONTACT:\s)(?:.*?)(\(*\d{3}\)*[- ]*\d{3}[- ]*\d{4}|Inspection)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"

#Gets contact information
def getContact(text):
	try:
		result = re.findall(r'(?:PERMIT CONTACT:\s*)(.*?)(?:\(*\d{3}\)*[- ]*\d{3}[- ]*\d{4}|Inspection)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"

#Gets address of company
def getLocation(text):
	try: 
		result = re.findall(r'(?:Location:\s*)(.*?)(?:PHONE:|Inspection|PERMIT)', text, re.DOTALL|re.MULTILINE)
		return result[0].strip()
	except Exception as E:
		return "error"

#Get yearly permit number
def getPermitNum(text):
	try: 
		result = re.findall(r'(AP\d{0,2}-\d{4})', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"

#Get state ID number
def getStateIDNum(text):
	try: 
		result = re.findall(r'(?:\d{2}\/\d{2}\/\d{4}\s*)([A-Z]{3}[- ]\d{5,6})', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"

#Get company name
def getCompanyName(text):
	try: 
		result = re.findall(r'(?:Location:\s*)(.*?)(P\.O\.|\d|PO BOX)', text, re.DOTALL|re.MULTILINE)
		return result[0][0].strip()
	except Exception as E:
		return "error"

#Get status: pass or fail
def getInspStatus(text):
	try: 
		result = re.findall(r'(Pass|Fail)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"

#Gets date of inspection
def getInspD8(text):
	try: 
		result = re.findall(r'(?:Inspector:\s*|Inspection Date:\s*)\s(\d{2}\/\d{2}\/\d{4})', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"

#Gets inspector name
def getInspector(text):
	try: 
		#pulls text
		result = re.findall(r'(?:GA-*\d{2}[- ]\d{4,5}|Annual Inspection\s\d*)(.*?)(?:Equip)', text, re.DOTALL|re.MULTILINE)
		
		#Strips other characters out of text
		clean_result = re.sub(r'(\d*)', '', result[0])
		clean_result = re.sub(r'(GA-*\s*)', '', clean_result)
		clean_result = re.sub(r'([-=(),.]*)', '', clean_result)
		clean_result = re.sub(r'(Permit Sticker No:)', '', clean_result)
		clean_result = re.sub(r'(Inspector:)', '', clean_result)
		return clean_result.strip()
	except Exception as E:
		return "error"	

#Gets permit expiration date
def getPermExpD8(text):
	try: 
		result = re.findall(r'(?:AP\d{0,2}-\d{4}\s*|Permit Expiration Date:\s*)(\d{2}\/\d{2}\/\d{4})', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"

#Returns annual inspection or blank
def getInspType(text):
	try: 
		result = re.findall(r'(Annual Inspection)', text, re.DOTALL|re.MULTILINE)
		return result[0].strip()
	except Exception as E:
		return "error"

#Gets GA permit sticker number
def getGAPermStickNum(text):
	try: 
		result = re.findall(r'(?:Annual Inspection\s|GA Permit Sticker No.:\s)(d{4}|(GA|AC)[- ]*\d{2}[- ]*\d{4,5}|G*A*[- ]*\d{3,7})', text, re.DOTALL|re.MULTILINE)
		return result[0][0]
	except Exception as E:
		return "error"	

#Gets contact info
def getContact(text):
	try: 
		result = re.findall(r'(PERMIT CONTACT:\s)(.*?\d{4})', text, re.DOTALL|re.MULTILINE)
		return result[0][1]
	except Exception as E:
		return "error"		

#Gets name of ride
def getRideName(text):
	try: 
		result = re.findall(r'(?:Ride:\s*)(.*?)\s*(Serial)', text, re.DOTALL|re.MULTILINE)
		return result[0][0]
	except Exception as E:
		return "error"	

#Gets name of manufacturer
def getManufacturer(text):
	try: 
		result = re.findall(r'(?:Manufacturer:\s*)(.*?)\s*(?:Manufacture Date|Serial)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"	

#Gets manufacture date
def getManufacturerD8(text):
	try: 
		result = re.findall(r'(?:Manufacture Date:\s*)(?:\S*?)(\d*)(?:\n*|Seating)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"	

#Gets seating capacity of ride
def getSeatingCapacity(text):
	try: 
		result = re.findall(r'(?:\nSeating Capacity:\s*)(.*?)\s*(?:Child Seating|Serial|Post)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"	

#Gets child seating capacity of ride
def getChildSeatingCapacity(text):
	try: 
		result = re.findall(r'(?:Child Seating Capacity:\s*)(.*?)\s*(?:Ride|\n)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"	

#Gets ride speed
def getRideSpeed(text):
	try: 
		result = re.findall(r'(?:Ride\s*Speed:\s*)(.*?)\s*(?:Post|\n)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as E:
		return "error"	

#Gets the serial number of ride
def getSerialNum(text):
	try: 
		result = re.findall(r'(?:Serial No\.:\s*)(.*?)\s*(\n)', text, re.DOTALL|re.MULTILINE)
		return result[0][0]
	except Exception as E:
		return "error"

#Takes text and returns a usaddress object
def cleanAddress(text):
	try:
		return usaddress.tag(text)
	except Exception as E:
		return "error"

#Gets the list of violations or returns None if none
def getViolations(text):
	try:
		result = re.sub(r'(Viol\.\s*\t*|Date\s*\t*|Correct By\s*\t*|Resolved\s*\t*|Comment\s*\t*)', '', text[0], re.DOTALL|re.MULTILINE)
		if (result != "None\r\n"):
			stuff = re.findall(r'(.*?)\t((\d{1,2}\/\d{1,2}\/\d{4}\s*)(?:12[:(0AM]*\t*))+(.*?)\r\n', result, re.DOTALL|re.MULTILINE)
			return stuff
		else: 
			return 'None'
	except Exception as e:
		print e
		return "Error"

#Gets comments after violations
def getPostRemarks(text):
	try:
		result = re.findall(r'(?:Post-Inspection Remarks:\s*)(.*?)(?:\Z)', text, re.DOTALL|re.MULTILINE)
		return result[0]
	except Exception as e:
		return "error"	



#Defines headers for file
headers = ["company_name", "full_address", "street", "city", "state", "zipcode", "county", "phone", "cont", "cont_phone", "insp_d8", "permit_num", "perm_exp_d8", "state_id_num", "insp_stat", "insp_type", "ga_perm_stick_num", "inspector", "ride_name", "manufacturer", "seating_cap", "serial_num", "manufacture_d8", "child_seating_cap", "speed", "post_remarks", "condition", "viol_d8", "correct_d8", "resolve_d8", "comment"]

#Creates output file with headers
create_output_file(output_file_name, headers)

i = 0
orig_file = read_file(file_name)

#Searches for records
try:
	for match in re.findall(r'(?:INSPECTION DETAILS)(.*?)(Division-Safety|\Z)', orig_file, re.DOTALL|re.MULTILINE):
		#initializes fields
		full_text = ''
		full_address = ''
		company_name=''
		street=''
		city=''
		state=''
		zipcode=''
		county=''
		phone=''
		cont=''
		cont_phone=''
		insp_d8=''
		permit_num=''
		perm_exp_d8=''
		insp_stat=''
		insp_type=''
		state_id_num=''
		ga_perm_stick_num=''
		inspector=''
		ride_name=''
		manufacturer=''
		seating_cap=''
		serial_num=''
		manufacture_d8=''
		child_seating_cap=''
		speed=''
		post_remarks=''
		condition=''
		viol_d8=''
		correct_d8=''
		resolve_d8=''
		comment=''


		full_text = match[0]

		#Gets shortened version of inspection record
		equipment = re.findall(r'(?:Equipment Information\s*)(.*?)(?:Conditions \/ Violations|\Z)', full_text, re.DOTALL|re.MULTILINE)
		conditions = re.findall(r'(?:Conditions \/ Violations\s*)(.*?)(?:Page 1|\Z)', full_text, re.DOTALL|re.MULTILINE)


		#Gets company information per inspection
		company_name=getCompanyName(full_text)
		full_address = getLocation(full_text)
		clean_address = cleanAddress(full_address)

		try:
			#Breaks apart a usaddress object into each component
			if ('AddressNumber' in clean_address[0]):
				street = street + " " + clean_address[0]['AddressNumber']
			if ('StreetNamePreDirectional' in clean_address[0]):
				street = street + " " + clean_address[0]['StreetNamePreDirectional']
			if ('StreetNamePreType' in clean_address[0]):
				street = street + " " + clean_address[0]['StreetNamePreType']
			if ('StreetName' in clean_address[0]):
				street = street + " " + clean_address[0]['StreetName']
			if ('StreetNamePostType' in clean_address[0]):
				street = street + " " + clean_address[0]['StreetNamePostType']
			if ('StreetNamePostDirectional' in clean_address[0]):
				street = street + " " + clean_address[0]['StreetNamePostDirectional']
			if ('StreetNamePostModifier' in clean_address[0]):
				street = street + " " + clean_address[0]['StreetNamePostModifier']
			if ('OccupancyType' in clean_address[0]):
				street = street + " " + clean_address[0]['OccupancyType']
			if ('OccupancyIdentifier' in clean_address[0]):
				street = street + " " + clean_address[0]['OccupancyIdentifier']	
			if ( 'USPSBoxType' in clean_address[0]):
				street = street + clean_address[0]['USPSBoxType']
			if ( 'USPSBoxID' in clean_address[0]):
				street = street + " " + clean_address[0]['USPSBoxID']
			if ('PlaceName' in clean_address[0]):
				city=clean_address[0]['PlaceName']
			if ('StateName' in clean_address[0]):
				state=clean_address[0]['StateName']
			if ('ZipCode' in clean_address[0]):
				zipcode=clean_address[0]['ZipCode']
			if ('CountryName' in clean_address[0]):
				county=clean_address[0]['CountryName']
		except Exception as f:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno, str(f))
		
		#Gets each item from file
		phone=getPhone(full_text)
		cont=getContact(full_text)
		cont_phone=getContactPhone(full_text)
		insp_d8=getInspD8(full_text)
		permit_num=getPermitNum(full_text)
		state_id_num=getStateIDNum(full_text)
		perm_exp_d8=getPermExpD8(full_text)
		insp_stat=getInspStatus(full_text)
		insp_type=getInspType(full_text)
		ga_perm_stick_num=getGAPermStickNum(full_text)
		inspector=getInspector(full_text)
		ride_name=getRideName(full_text)
		manufacturer=getManufacturer(equipment[0])
		seating_cap=getSeatingCapacity(equipment[0])
		serial_num=getSerialNum(equipment[0])
		manufacture_d8=getManufacturerD8(equipment[0])
		child_seating_cap=getChildSeatingCapacity(equipment[0])
		speed=getRideSpeed(equipment[0])
		post_remarks=getPostRemarks(equipment[0])
		condition_result = []
		condition_result = getViolations(conditions)

		#Breaks apart conditions into the comment and condition 
		if (condition_result != "None" and len(condition_result) != 0):
			for c in condition_result:
				condition = ''
				viol_d8 = ''
				correct_d8 = ''
				resolve_d8 = ''
				comment = ''
				print("Length: ", len(c))
				if(len(c) > 1):
					print("length greater than 1")
					condition=c[0]
					comment= c[len(c)-1]

				#For each violation, iterates through the various header fields, adds to row list, and amends ot the output file 
				row = []
				for l in headers:
					row.append(eval(l))
				print row
				amend_file(output_file_name, row)
		elif (condition_result == "None"):
			condition = "None"

			row = []
			#Iterates through header fields and amends to file
			for l in headers:
				row.append(eval(l))
			amend_file(output_file_name, row)
		else:
			condition = "Error"
			row = []
			#Iterates through header fields and amends to file
			for l in headers:
				row.append(eval(l))
			amend_file(output_file_name, row)
			
		i = i+1
except Exception as e:
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(exc_type, fname, exc_tb.tb_lineno, str(e))


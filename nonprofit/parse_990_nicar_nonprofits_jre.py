'''
Parses 2017 data to pull highest paid employees, filing information and loans to interested persons 

This parser builds upon Todd Wallack's parser from the Boston Globe
Find his original code here https://github.com/TWALLACK/IRS

Each year the different tags that are used in the XML document change, so before running,
you'll want to check the tags to see they are all the same
'''

# import modules
import xmltodict, json, requests, re, os, time, csv, xml.etree.ElementTree as xml

#Define initial variables
year = 16  #Two Digit Year Between 11 and 18
current_path = os.getcwd()  #looks up current working directory
path = "./IRS/filings_" + str(year) #This is where files are stored
path_out = os.getcwd() + "\\" #This is where the output files are stored


#initializes headers for output file
headers_main = []
headers_loan = []
headers_highest_paid = []
row_main = []
headers_file = ["url"]
file_row_main = []

#This sets what data you are gathering 
versions = ["all", "loan", "nonprofit", "top_paid_employees"] #each corresponds to a function above
version = versions[0] #update to change state

#Sets the output file
main_file = path_out + 'main_' + str(year) + '.csv'
loan_file = path_out + 'loan_' + str(year) + '.csv'
highest_paid_file = path_out + 'highest_paid_' + str(year) + '.csv'
files = path_out + 'file_' + str(year) + '.csv'
read_files = []

# Creates output file based on headers
def create_output_file(output_file,headers):
    with open(output_file,'wb') as csv_output:
        rowwriter = csv.writer(csv_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)  
        rowwriter.writerow(headers)

# Amends to output file
def amend_output_file(output_file,new_line):
    with open(output_file,'ab') as csv_output:
        rowwriter = csv.writer(csv_output, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)  
        rowwriter.writerow(new_line)




# Build a list of the 990 files already stored in directory
filing_list = [ i for i in os.listdir(path) if i[-4:] == 'html' ] #gets all documents that end in .html in current year folder, can only look at one year at a time
filings = str(len(filing_list))
print "There are " + str(filings) + " filings in the folder."

#grab text in tag
def grab_text(regex,web_page):
    match = re.search(regex,web_page)
    if match:
        tag = match.group(1)
    else:
        tag = ""
    return tag

#grab multiple pieces of text in tag
def grab_texts(regex,web_page,fields):
    match = re.search(regex,web_page)
    tags = []
    if match:
        for field in range(fields):
            tags.append(match.group(field + 1))
            tags.append(" ")
    else:
        for field in range(fields):
            tags.append("")
    return tags


# Function to grab basic filer info from 990 
def grab_filer_info(page, url):
    global bus_name,ein,city,state,zipcode,address,tax_period_begin,tax_period_end,signature_date,return_date,amended,return_type,tax_year
    #reset variables used in function
    bus_name = ""
    ein = ""  
    address_info =[]  #Sets up empty bucket for address info
    zipcode = ""
    state = ""
    city = ""
    address = ""
    file_row_main = []
    try: 
        o = xmltodict.parse(page)
        try:
            #Gets business name
            dict= o['Return']['ReturnHeader']['Filer']['BusinessName']
        except Exception:
            #Gets filer name
            dict = o['Return']['ReturnHeader']['Filer']['Name']
        for key, value in dict.iteritems():
            bus_name += value
            bus_name.replace('"', '\'')  
        #Gets ein - unique to each business per filing year
        ein = o['Return']['ReturnHeader']['Filer']['EIN'].strip()
        try:
            #Gets business US address
            dict= o['Return']['ReturnHeader']['Filer']['USAddress']
            for key, value in dict.iteritems():
                address_info.append(value)
            zipcode = address_info.pop()
            state = address_info.pop()
            city = address_info.pop()
            for info in address_info:
                address += info
        except KeyError:
            #Gets foreign address
            dict= o['Return']['ReturnHeader']['Filer']['ForeignAddress']
            address_info = ""
            for key, value in dict.iteritems():
                address_info += value
            ziocode = ""
            city = ""
            state = ""
            address = address_info
        #Gets other filing info
        tax_period_begin = grab_text(r'>([^<]*)</TaxPeriodBegin(?:Dt|Date)>',page).strip()
        tax_period_end = grab_text(r'>([^<]*)</TaxPeriodEnd(?:Dt|Date)>',page).strip()
        signature_date = grab_text(r'>([^<]*)</(Signature(?:Dt|Date)?|DateSigned)>',page).strip()
        return_date = grab_text(r'>([^<]*)</(?:ReturnTs|Timestamp)>',page).strip()
        amended = grab_text(r'>([^<]*)</AmendedReturn(?:Ind)?>',page).strip()
        return_type = grab_text(r'>([^<]*)</ReturnType(?:C)?[A-z]*>',page).strip()
        tax_year = grab_text(r'<TaxY(?:ea)?r>([^<]*)</TaxY(?:ea)?r>',page).strip()
    except Exception:
        file_row_main.append("ERROR: " + url)
        amend_output_file(files, file_row_main)



#This function gets load to interested parties 
def getLoan(file, page):
    #initializes variables
    global name, relation, purpose, loan_to_org, loan_from_org, original_amount, balance_due_amount, default_ind, approved_by_board, written_agreement
    name=''
    relation='' 
    purpose=''
    loan_to_org=''
    loan_from_org=''
    original_amount=''
    balance_due_amount=''
    default_ind='' 
    approved_by_board='' 
    written_agreement=''

    #Sees if there are any loans to individuals
    match = re.search(r'>([^<]*)</LoanOutstandingInd(?:Ind)?>',page)
    loan = ""

    # if match, parse through
    if match:
        loan = match.group(1)
        #If loan exists
        if loan == "1" or loan.upper() == "TRUE":
            try:
                tree = xml.parse(file)
                for l in tree.find('{http://www.irs.gov/efile}ReturnData'):

                    #Checks to see if Schedule L exists, which is where loans are 
                    if(l.tag == '{http://www.irs.gov/efile}IRS990ScheduleL'):

                        #Loops for each person in loans between interested party 
                        for m in l.findall('{http://www.irs.gov/efile}LoansBtwnOrgInterestedPrsnGrp'):
                            #Gets name of person receiving loan
                            if m.find('{http://www.irs.gov/efile}PersonNm') is not None:
                                name = m.find('{http://www.irs.gov/efile}PersonNm').text.strip()
                            
                            #Gets relation of person getting loan 
                            if m.find('{http://www.irs.gov/efile}RelationshipWithOrgTxt') is not None:
                                relation = m.find('{http://www.irs.gov/efile}RelationshipWithOrgTxt').text.strip()
                            
                            #Gets purpose of loan text
                            if m.find('{http://www.irs.gov/efile}LoanPurposeTxt') is not None:
                                purpose = m.find('{http://www.irs.gov/efile}LoanPurposeTxt').text.strip()
                            
                            #Is the loan to the org?
                            if m.find('{http://www.irs.gov/efile}LoanToOrganizationInd') is not None:
                                if m.find('{http://www.irs.gov/efile}LoanToOrganizationInd').text.strip() == "X":
                                    loan_to_org=1
                                else:
                                    loan_to_org=0
                            else:
                                loan_to_org=0
                            
                            #Is the loan to the ind?
                            if m.find('{http://www.irs.gov/efile}LoanFromOrganizationInd') is not None:
                                if m.find('{http://www.irs.gov/efile}LoanFromOrganizationInd').text.strip() == "X":
                                    loan_from_org=1
                                else:
                                    loan_from_org=0
                            else: 
                                loan_from_org=0

                            #Amount of loan
                            if m.find('{http://www.irs.gov/efile}OriginalPrincipalAmt') is not None:
                                original_amount=int(m.find('{http://www.irs.gov/efile}OriginalPrincipalAmt').text.strip())

                            #Amount of loan still to be paid 
                            if m.find('{http://www.irs.gov/efile}BalanceDueAmt') is not None:
                                balance_due_amount=int(m.find('{http://www.irs.gov/efile}BalanceDueAmt').text.strip())

                            if m.find('{http://www.irs.gov/efile}DefaultInd') is not None:
                                default_ind=m.find('{http://www.irs.gov/efile}DefaultInd').text.strip()

                            #Did board approve loan?
                            if m.find('{http://www.irs.gov/efile}BoardOrCommitteeApprovalInd') is not None:
                                approved_by_board=m.find('{http://www.irs.gov/efile}BoardOrCommitteeApprovalInd').text.strip()

                            #Was there written approval for loan?
                            if m.find('{http://www.irs.gov/efile}WrittenAgreementInd') is not None:
                                written_agreement= m.find('{http://www.irs.gov/efile}WrittenAgreementInd').text.strip()

                            #Make a row of the interested fields and amend to the output file
                            row_main = []
                            for header in headers_loan:
                                if name:
                                    row_main.append(eval(header))  #add every field in heards to new row
                            amend_output_file(loan_file,row_main)

                            #Sets vars to NULL
                            name=''
                            relation='' 
                            purpose=''
                            loan_to_org=''
                            loan_from_org=''
                            original_amount=''
                            balance_due_amount=''
                            default_ind='' 
                            approved_by_board='' 
                            written_agreement=''
            except Exception:
                file_row_main.append("ERROR: " + url)
                amend_output_file(files, file_row_main)
    else:
        loan=""


#This function gets the top paid employees
def getTopPaid(file, page):
    #searches the two spots where top paid employee information is stored
    match = re.search(r'>([^<]*)</LoanOutstanding(?:Ind)?>',page)
    ceo_comp = re.search(r'>([^<]*)</CompensationProcessCEO(?:Ind)?>',page)
    ind_comp = re.search(r'>([^<]*)</CompensationProcessOther(?:Ind)?>',page)
    high_comp = re.search(r'>([^<]*)</TotalCompGreaterThan150K(?:Ind)?>',page)

    #Declare and initialize variables
    global name, title, compensation, compensation_j, comp_related_j, other_comp_j, hours_per_week, total_comp_related, ind_trustee_or_dir, officer, inst_trustee, key_employee, highest_comp_employee , former , comp_related, other_comp, bonus_filing, bonus_related, other_comp_related, deferred_comp, deferred_comp_related, nontax_benefits, nontax_benefits_related, comp_prior, comp_prior_related

    name=''
    title='' 
    compensation=''
    compensation_j=''
    hours_per_week=''
    total_comp_related = ''
    ind_trustee_or_dir=''
    officer=''
    inst_trustee=''
    key_employee=''
    highest_comp_employee='' 
    former='' 
    comp_related=''
    comp_related_j=''
    other_comp=''
    other_comp_j= ''
    bonus_filing = ''
    bonus_related = ''
    other_comp_related = ''
    deferred_comp = ''
    deferred_comp_related = ''
    nontax_benefits = ''
    nontax_benefits_related = ''
    comp_prior = ''
    comp_prior_related = ''

    #Parse tree for income data in 990 form
    try: 
        tree = xml.parse(file)
        for l in tree.find('{http://www.irs.gov/efile}ReturnData'):
            if(l.tag == '{http://www.irs.gov/efile}IRS990'):
                #Looks for Part VII Section A where highest compensated employee/board members is stored
                for m in l.findall('{http://www.irs.gov/efile}Form990PartVIISectionAGrp'): #some also use sectionA

                    if m.find('{http://www.irs.gov/efile}PersonNm') is not None:
                        name = m.find('{http://www.irs.gov/efile}PersonNm').text
                    print("in title part", name)
                    
                    if m.find('{http://www.irs.gov/efile}TitleTxt') is not None:
                        title = m.find('{http://www.irs.gov/efile}TitleTxt').text
                    
                    if m.find('{http://www.irs.gov/efile}AverageHoursPerWeekRt') is not None:
                        hours_per_week = m.find('{http://www.irs.gov/efile}AverageHoursPerWeekRt').text
                    
                    if m.find('{http://www.irs.gov/efile}IndividualTrusteeOrDirectorInd') is not None:
                        if m.find('{http://www.irs.gov/efile}IndividualTrusteeOrDirectorInd').text == "X":
                            ind_trustee_or_dir=1
                        else:
                            ind_trustee_or_dir=0
                    
                    if m.find('{http://www.irs.gov/efile}InstitutionalTrusteeInd') is not None:
                        if m.find('{http://www.irs.gov/efile}InstitutionalTrusteeInd').text == "X":
                            inst_trustee=1
                        else:
                            inst_trustee=0

                    if m.find('{http://www.irs.gov/efile}OfficerInd') is not None:
                        if m.find('{http://www.irs.gov/efile}OfficerInd').text == "X":
                            officer=1
                        else:
                            officer=0

                    if m.find('{http://www.irs.gov/efile}FormerOfcrDirectorTrusteeInd') is not None:
                        if m.find('{http://www.irs.gov/efile}FormerOfcrDirectorTrusteeInd').text == "X":
                            former=1
                        else:
                            former=0

                    if m.find('{http://www.irs.gov/efile}HighestCompensatedEmployeeInd') is not None:
                        if m.find('{http://www.irs.gov/efile}HighestCompensatedEmployeeInd').text == "X":
                            highest_comp_employee=1
                        else:
                            highest_comp_employee=0

                    if m.find('{http://www.irs.gov/efile}KeyEmployeeInd') is not None:
                        if m.find('{http://www.irs.gov/efile}KeyEmployeeInd').text.strip() == "X":
                            key_employee=1
                        else:
                            key_employee=0

                    if m.find('{http://www.irs.gov/efile}ReportableCompFromOrgAmt') is not None:
                        compensation=int(m.find('{http://www.irs.gov/efile}ReportableCompFromOrgAmt').text)

                    if m.find('{http://www.irs.gov/efile}ReportableCompFromRltdOrgAmt') is not None:
                        comp_related=int(m.find('{http://www.irs.gov/efile}ReportableCompFromRltdOrgAmt').text)

                    if m.find('{http://www.irs.gov/efile}OtherCompensationAmt') is not None:
                        other_comp=m.find('{http://www.irs.gov/efile}OtherCompensationAmt').text
                    
                    row_main = []
                    #Takes the interested fields and says them to row to amend to the file
                    for header in headers_highest_paid:
                        if name :
                            row_main.append(eval(header))  #add every field in heards to new row
                    amend_output_file(highest_paid_file,row_main)
                    name=''
                    title='' 
                    hours_per_week=''
                    ind_trustee_or_dir=''
                    officer=''
                    inst_trustee=''
                    key_employee=''
                    highest_comp_employee='' 
                    former='' 
                    compensation=''
                    comp_related=''
                    other_comp=''
    except Exception:
        file_row_main.append("ERROR: " + url)
        amend_output_file(files, file_row_main)

    #If the highest compensated employees is available
    if high_comp:

        high_comp = match.group(1)
        if high_comp == "1" or high_comp.upper() == "TRUE":
            try:
                tree = xml.parse(file)
                for l in tree.find('{http://www.irs.gov/efile}ReturnData'):
                    #Searches for Schedule J, where compensated ind over 100k is housed
                    if(l.tag == '{http://www.irs.gov/efile}IRS990ScheduleJ'):
                        for m in l.findall('{http://www.irs.gov/efile}RltdOrgOfficerTrstKeyEmplGrp'):
                            
                            if m.find('{http://www.irs.gov/efile}PersonNm') is not None:
                                name = m.find('{http://www.irs.gov/efile}PersonNm').text.strip()
                            print("in highest comp", name)
                            if m.find('{http://www.irs.gov/efile}TitleTxt') is not None:
                                title = m.find('{http://www.irs.gov/efile}TitleTxt').text.strip()
                            
                            if m.find('{http://www.irs.gov/efile}BaseCompensationFilingOrgAmt') is not None:
                                compensation_j = m.find('{http://www.irs.gov/efile}BaseCompensationFilingOrgAmt').text.strip()
                            
                            if m.find('{http://www.irs.gov/efile}CompensationBasedOnRltdOrgsAmt') is not None:
                                comp_related_j = m.find('{http://www.irs.gov/efile}CompensationBasedOnRltdOrgsAmt').text.strip()

                            if m.find('{http://www.irs.gov/efile}BonusFilingOrganizationAmount') is not None:
                                bonus_filing=int(m.find('{http://www.irs.gov/efile}BonusFilingOrganizationAmount').text.strip())

                            if m.find('{http://www.irs.gov/efile}BonusRelatedOrganizationsAmt') is not None:
                                bonus_related=int(m.find('{http://www.irs.gov/efile}BonusRelatedOrganizationsAmt').text.strip())

                            if m.find('{http://www.irs.gov/efile}OtherCompensationFilingOrgAmt') is not None:
                                other_comp_j=m.find('{http://www.irs.gov/efile}OtherCompensationFilingOrgAmt').text.strip()

                            if m.find('{http://www.irs.gov/efile}OtherCompensationRltdOrgsAmt') is not None:
                                other_comp_related=m.find('{http://www.irs.gov/efile}OtherCompensationRltdOrgsAmt').text.strip()

                            if m.find('{http://www.irs.gov/efile}DeferredCompensationFlngOrgAmt') is not None:
                                deferred_comp= m.find('{http://www.irs.gov/efile}DeferredCompensationFlngOrgAmt').text.strip()

                            if m.find('{http://www.irs.gov/efile}DeferredCompRltdOrgsAmt') is not None:
                                deferred_comp_related = m.find('{http://www.irs.gov/efile}DeferredCompRltdOrgsAmt').text.strip()

                            if m.find('{http://www.irs.gov/efile}NontaxableBenefitsFilingOrgAmt') is not None:
                                nontax_benefits =int(m.find('{http://www.irs.gov/efile}NontaxableBenefitsFilingOrgAmt').text.strip())

                            if m.find('{http://www.irs.gov/efile}NontaxableBenefitsRltdOrgsAmt') is not None:
                                nontax_benefits_related =int(m.find('{http://www.irs.gov/efile}NontaxableBenefitsRltdOrgsAmt').text.strip())

                            if m.find('{http://www.irs.gov/efile}TotalCompensationRltdOrgsAmt') is not None:
                                total_comp_related =m.find('{http://www.irs.gov/efile}TotalCompensationRltdOrgsAmt').text.strip()

                            if m.find('{http://www.irs.gov/efile}CompReportPrior990FilingOrgAmt') is not None:
                                comp_prior =m.find('{http://www.irs.gov/efile}CompReportPrior990FilingOrgAmt').text.strip()

                            if m.find('{http://www.irs.gov/efile}CompReportPrior990RltdOrgsAmt') is not None:
                                comp_prior_related = m.find('{http://www.irs.gov/efile}CompReportPrior990RltdOrgsAmt').text.strip()

                            row_main = []
                            #Takes the interested fields and says them to row to amend to the file
                            for header in headers_highest_paid:
                                if name :
                                    row_main.append(eval(header))
                            amend_output_file(highest_paid_file,row_main)

                            #Sets fields to NULL
                            name = ''
                            title = ''
                            compensation_j = ''
                            comp_related_j = ''
                            bonus_filing = ''
                            bonus_related = ''
                            other_comp_j = ''
                            other_comp_related = ''
                            deferred_comp = ''
                            deferred_comp_related = ''
                            nontax_benefits = ''
                            nontax_benefits_related = ''
                            total_comp_related = ''
                            comp_prior = ''
                            comp_prior_related = ''
            except Exception:
                #ERROR: url when an exception occurs
                file_row_main.append("ERROR: " + url)
                amend_output_file(files, file_row_main)

# this function parses body of 990
def parse_990(page,url, file):
    grab_filer_info(page, url) #grabs business info and stores in global var
    match = re.search(r'>([^<]*)</Organization501c3(?:Ind)?>',page)
    match2 = re.search(r'<Organization501cInd\s*organization501cTypeTxt=\"(\d*)\">([^<]*)</Organization501cInd>',page)
    match3 = re.search(r'<Organization501c3(?:Ind)?[^>]*>([^<]*)</Organization501c3(?:Ind)?>',page)
    match4 = re.search(r'<Organization4947a1NotPF(?:Ind)?>([^<]*)</Organization4947a1NotPF(?:Ind)?>',page)
    match5 = re.search(r'<Organization501c\s*typeOf501cOrganization=\"(\d*)\">([^<]*)</Organization501c>',page)
    if match:
        organization = "501c3"
        organization_flag = match.group(1)
    elif match2:
        organization = "501c" + match2.group(1)
        organization_flag = match2.group(2)
    elif match3:
        organization = "501c3" 
        organization_flag = match3.group(1)
    elif match4:
        organization = "4947a1"
        organization_flag = match4.group(1)
    elif match5:
        organization = "501c" + match5.group(1)
        organization_flag = match5.group(2)
    else:
        organization = ""
        organization_flag = ""


   # This section grabs several key fields from forms. You can easily add others
    formation = grab_text(r'>([^<]*)</(?:YearFormation|Formation(?:Yr|Year))>',page)
    domicile_state = grab_text(r'>([^<]*)</(?:StateLegalDomicile|LegalDomicileState[A-z]*)>',page)
    cy_revenue =grab_text(r'>([^<]*)</(?:CYTotalRevenueAmt|TotalRevenueCurrentYear)',page)

    #determines what information is getting parsed based on version which is set above
    if (version == "loan"):
        getLoan(file, page)
    elif (version == "top_paid_employees"):
        getTopPaid(file, page)
    elif (version == "nonprofit"):
        row_main = []
        for header in headers_main:
            if (ein != ''):
                row_main.append(eval(header))  #add every field in heards to new row
        amend_output_file(main_file,row_main)
    else: 
        getLoan(file, page)
        getTopPaid(file, page)
        row_main = []
        for header in headers_main:
            if (ein != ''):
                row_main.append(eval(header))  #add every field in heards to new row
        amend_output_file(main_file,row_main)

    


#This sets the headers depending on what data you are trying to
if (version == "loan"):
    headers_loan = ["bus_name","ein", "url", "tax_period_begin", "tax_period_end","tax_year", "signature_date", "return_date", "amended", "return_type", "name", "relation", "purpose", "loan_to_org", "loan_from_org", "original_amount", "balance_due_amount", "default_ind", "approved_by_board", "written_agreement"]
    create_output_file(loan_file,headers_loan)
elif (version == "nonprofit"):
    headers_main = ["bus_name","ein","url", "city","state","zipcode","address","tax_period_begin", "tax_period_end","tax_year", "signature_date", "return_date", "amended", "return_type"]
    #save headers to the output file
    amend_output_file(main_file,headers_main)
elif (version == "top_paid_employees"):
    headers_highest_paid = ["bus_name","ein", "url", "tax_period_begin", "tax_period_end","tax_year", "signature_date", "return_date", "amended","return_type", "name", "title", "compensation", "hours_per_week", "total_comp_related", "ind_trustee_or_dir", "officer", "inst_trustee", "key_employee", "highest_comp_employee ", "former ", "comp_related", "other_comp", "compensation_j", "comp_related_j", "bonus_filing", "bonus_related", "other_comp_j", "other_comp_related", "deferred_comp", "deferred_comp_related", "nontax_benefits", "nontax_benefits_related", "comp_prior", "comp_prior_related"]
    create_output_file(highest_paid_file,headers_highest_paid)
else: 
    #save headers to the output file
    headers_loan = ["bus_name","ein", "url", "tax_period_begin", "tax_period_end","tax_year", "signature_date", "return_date", "amended", "return_type", "name", "relation", "purpose", "loan_to_org", "loan_from_org", "original_amount", "balance_due_amount", "default_ind", "approved_by_board", "written_agreement"]
    headers_highest_paid = ["bus_name","ein", "url", "tax_period_begin", "tax_period_end","tax_year", "signature_date", "return_date", "amended","return_type", "name", "title", "compensation", "hours_per_week", "total_comp_related", "ind_trustee_or_dir", "officer", "inst_trustee", "key_employee", "highest_comp_employee ", "former ", "comp_related", "other_comp", "compensation_j", "comp_related_j", "bonus_filing", "bonus_related", "other_comp_j", "other_comp_related", "deferred_comp", "deferred_comp_related", "nontax_benefits", "nontax_benefits_related", "comp_prior", "comp_prior_related"]
    headers_main = ["bus_name","ein","url", "city","state","zipcode","address","tax_period_begin", "tax_period_end","tax_year", "signature_date", "return_date", "amended", "return_type"]

    # Command to create output files, a different file per topic
    create_output_file(main_file,headers_main)
    create_output_file(loan_file,headers_loan)
    create_output_file(highest_paid_file,headers_highest_paid)
    create_output_file(files,headers_file)




#loops for each file in folder/filing list
for filing in filing_list:
    file_row_main = []
    new_path = path + "/" + filing
    infile = open(new_path) #opens each file for the year 
    web_page = infile.read() #gets contents that are in the file and saves to web_page
    url = "https://s3.amazonaws.com/irs-form-990/" + filing[:-5] + "_public.xml"
    print(url + "start")
    file_row_main.append(url)
    amend_output_file(files, file_row_main)
    match = re.search(r'<ReturnType(?:Cd)?>([^<]*)</ReturnType(?:Cd)?>',web_page) #check to make sure title is the same
    if match:
        ReturnTypeCd = match.group(1) #so what does this do 
        if ReturnTypeCd in ('990','990EO','990O'):
            parse_990(web_page,url, new_path)
        else:
            pass
    print(url + "done")

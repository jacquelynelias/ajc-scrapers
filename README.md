# Scrapers and parsers by Jacquelyn Elias - Updated November 2018

##Pardons
This project used pardon documents acquired through public records requests. The data came back in a .csv and paper copies. The paper copies were scanned, saved as pdf and then converted to .txt. The pardon.py script was used to take the .txt from the paper copies and pull out the relevant information into a .csv. The other two scripts were then used to split the different offenses and sentences, which were in one field. To total the number of different offenses, each offense had its own row even if it was from the same pardon case. 

##Nonprofit
The idea for this project came from Todd Wallack's work for the Boston Globe. We then built upon his parser, which you can find at https://github.com/TWALLACK/IRS. The IRS now publishes XML documents of 990 submissions online. This set is not complete; however, it does have several thousands of filings. 

Each year, some of the tags in the XML document change, so these will need to be adjusted for the libraries to be able to find the correct tag.

Note: you need to download all the XML files from the IRS files before running this scraper, which takes a significant amount of storage and time. 

###Run
To run, insert the correct year at 'year' at the top of the file and insert the correct file path at 'path' to the downloaded XML files. Todd's repository has a script to download these files. You can then run by putting into the terminal "python parse_990_nicar_nonprofits_jre.py"

##Rollercoaster Inspections
The data for this project came in two different pdfs of inspections of both carnival and amusement rides acquired through public record requests, which were then coverted to .txt. Two different scripts were then written to use regex to pull out the desired fields and two .csv were created. 

###Run
To run, insert the file name at the top of the file and run "python amus.py or python carnival.py" depending on which inspections you are looking through. 

###Cleaning
Before inserting into the warehouse, I went through the violations to check if they were properly formatted. I added the following fields:
park_id = each park is given an ID. Check the previous year inspection to find
page_num = I added this when cleaning to easily check which page the inspection was on
cond_num = this is a number associated to each violation such as "rails", "electrical", etc.. I found that sometimes the violations would be mispelled, so this allowed a way to count how many of each violations there are.

When you are ready to insert into the warehouse, there are sql scripts in the G drive.

###Web App
The link to the frontend of the app is https://bitbucket.org/ajcnewsapp/rides-inspections-frontend/src/master/
The link to the backend of the app is https://bitbucket.org/ajcnewsapp/ride-inspections-api/src/master/

###Caution
This pulls the relevant information by doing regex matches. Depending on the format of the inspections, this may change by year to year. 

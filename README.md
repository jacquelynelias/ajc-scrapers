# Scrapers and parsers by Jacquelyn Elias - Updated August 2018

##Pardons
This project used pardon documents acquired through public records requests. The data came back in a .csv and paper copies. The paper copies were scanned, saved as pdf and then converted to .txt. The pardon.py script was used to take the .txt from the paper copies and pull out the relevant information into a .csv. The other two scripts were then used to split the different offenses and sentences, which were in one field. To total the number of different offenses, each offense had its own row even if it was from the same pardon case. 

##Nonprofit
The idea for this project came from Todd Wallack's work for the Boston Globe. We then built upon his parser, which you can find at https://github.com/TWALLACK/IRS. The IRS now publishes XML documents of 990 submissions online. This set is not complete; however, it does have several thousands of filings. 

Each year, some of the tags in the XML document change, so these will need to be adjusted for the libraries to be able to find the correct tag.

Note: you need to download all the XML files from the IRS files before running this scraper, which takes a significant amount of storage and time. 

##Rollercoaster Inspections
The data for this project came in two different pdfs of inspections of both carnival and amusement rides acquired through public record requests, which were then coverted to .txt. Two different scripts were then written to use regex to pull out the desired fields and two .csv were created. 


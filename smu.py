# Sharepoint Migration Utilities

import os;
import traceback;
import logging;
from sys import argv;
from datetime import datetime;

LOG_NAME = 'smu_log.txt'
log_file = None
LAYOUT_REPORT = '"TransactionId","Timestamp","SourcePath","SourceBasename","SourceType","SourceSize","SourceModifiedAt","SourceCreatedAt","SourceAclsTotal","SourceAccessedAt","ResultCode","SourceExtension"';

'''

[0]	TransactionId
[1]	Timestamp
[2]	SourcePath
[3]	SourceBasename
[4]	SourceType
[5]	SourceSize
[6]	SourceModifiedAt
[7]	SourceCreatedAt
[8]	SourceAclsTotal
[9]	SourceAccessedAt
[10]ResultCode
[11]SourceExtension

'''

def validate_file(fileNameArg):
	if os.path.exists(fileNameArg) and os.path.isfile(fileNameArg):
		#print("File "+ fileNameArg +" OK")
		return True
	else:
		#print("File \""+ fileNameArg + "\" not exists")
		return False

def validate_file_layout(text):
	if text.strip().replace('\"','').replace('\ufeff', '')==LAYOUT_REPORT.strip().replace('\"','').replace('\ufeff', ''):

		return True
	else:
		print(LAYOUT_REPORT.strip().replace('\"',''))
		print(len(LAYOUT_REPORT.strip().replace('\"','')))
		print(text.strip().replace('\"',''))
		print(text.strip().replace('\"','').split())
		print(len(text.strip().replace('\"','')))
		return False

def analyze_results(linesArg):
	success = 0;
	errInvalidFileName = 0;
	warnEmpty = 0;
	errPath = 0;
	totalLinesCount = 0;

	for line in linesArg:
		line = line.replace('\"','')
		totalLinesCount += 1;
		columns = line.split(',');

		if columns[10].strip()=='':
			success+=1;
		elif columns[10].strip()=='PATH_LEN_GT_300':
			errPath+=1;
		elif columns[10].strip()=='ITEM_IS_EMPTY':
			warnEmpty+=1;
		elif columns[10].strip()=='INVALID_SHAREPOINT_NAME':
			errInvalidFileName+=1;

	return { 'success':success, 
			'errInvalidFileName':errInvalidFileName, 
			'warnEmpty':warnEmpty, 
			'errPath':errPath, 
			'totalLinesCount':totalLinesCount };

def fingerprint(results):

	print("Statistics of \'" + fileName + "\'")

	for key in results.keys():
		print("\tStatus " + key + ": " + str(results[key]))

def print_menu():
	print("What would you like to do?")
	print("\t1) Process Empty Files")
	print("\t2) Process Invalid Sharepoint Names")
	print("\t3) Process Long Paths (GT 300)")
	print("\t4) Log results and exit")
	print("\t5) Show results on screen")
	print("\t6) Only exit")

def opt4_log_results(fileName, results):
	results['file'] = fileName
	log("Results of file " + fileName + ":" + str(results));

def get_log_file():
	global log_file
	if log_file is None:
		log_file = open(LOG_NAME,'a');
	
	return log_file

def log(text):
	now = datetime.now();
	dt = now.strftime("%Y-%m-%d %H:%M:%S");
	get_log_file().write(dt + ' -- ' + text + '\n');

def close_log():
	log_file.close();


fileName = argv[1];

try:
	log('Starting SMU program...')

	# Validate if file exists
	if validate_file(fileName):
		print("File "+ fileName +" OK")

		with open(fileName) as file:
			lines = file.read().splitlines();

			if validate_file_layout(lines[0]):
				print("File layout OK\n")

				results = analyze_results(lines)

				fingerprint(results)
				print("\n\n")

				print_menu();

				option = input("\n\nWhich Option? ")
				again = True

				while True:

					if option == '1':
						log('1')
						again = False

					elif option == '2':
						log('2')
						again = False
					elif option == '3':
						log('3')
						again = False
					elif option == '5':
						log('5')
						fingerprint(results)
						again = False
					elif option == '4':
						log('4')
						opt4_log_results(fileName, results);
						break;
					elif option == '6':
						log('6')
						break;

					if again :
						option = input("\nSorry... Which option? ")
					else:
						again = True
						option = input("\nWe came back to the start. Which option now? ")

					# Program Final
				
			else:
				print("Invalid file layout")
	else:
		print("File \""+ fileName + "\" not exists")

except Exception as e:
	logging.error(traceback.format_exc())

finally:
	log('Closing program...');
	close_log();
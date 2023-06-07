# Sharepoint Migration Utilities

import os;
import traceback;
import logging;
import pandas;
from sys import argv;
from datetime import datetime;
from pyautogui import typewrite;

LOG_NAME = 'smu_log.txt'
log_file = None
LOG_RESULTS_NAME = 'smu_results.csv'
log_results_file = None
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

# ========= FUNCTIONS START ============ #

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

def opt1_empty_files(fileName):
	df = pandas.read_csv(fileName);

	df_filtered = df.query("ResultCode == 'ITEM_IS_EMPTY'");

	for index, row in df_filtered.iterrows():
		#print(row['SourcePath']);
		itemFilePath = row['SourcePath'];

		# Check if File still exists
		if (validate_file(itemFilePath)):
			if(os.path.getsize(itemFilePath) == 0):
				log("The path {} is a empty file and is going to be deleted".format(itemFilePath));
				os.remove(itemFilePath);
				log_result(fileName, itemFilePath, "ITEM_IS_EMPTY", "DELETE", "The path {} is a empty file and is going to be deleted".format(itemFilePath));
		else:
			log("The path {} is not a file or does not exist".format(itemFilePath))
			log_result(fileName, itemFilePath, "ITEM_IS_EMPTY", "SKIP", "The path {} is not a file or does not exist".format(itemFilePath));

def opt2_invalid_names(fileName):
	df = pandas.read_csv(fileName);

	df_filtered = df.query("ResultCode == 'INVALID_SHAREPOINT_NAME'");

	for index, row in df_filtered.iterrows():
		itemFilePath = row['SourcePath'];
		itemName = row['SourceBasename'];
		itemFilePathLen = len(itemFilePath);

		# Check if File still exists
		if (validate_file(itemFilePath)):
			if(itemName.startswith("~$")):
				if(opt2_check_similarity(itemFilePath)):
					log("The path {} is a TEMP file and is going to be deleted".format(itemFilePath))
					os.remove(itemFilePath);
					log_result(fileName, itemFilePath, "INVALID_SHAREPOINT_NAME", "DELETE", "The path {} is a TEMP file and is going to be deleted".format(itemFilePath));
				elif opt2_check_tiny_file(itemFilePath):
					log("The path {} is a TEMP and TINY file and is going to be deleted".format(itemFilePath))
					os.remove(itemFilePath);
					log_result(fileName, itemFilePath, "INVALID_SHAREPOINT_NAME", "DELETE", "The path {} is a TEMP and TINY file and is going to be deleted".format(itemFilePath));
				else:
					log_result(fileName, itemFilePath, "INVALID_SHAREPOINT_NAME", "RENAME PROMPT", "");
					rename_file(itemFilePath);
					
			else:
				if (itemFilePath.endswith("desktop.ini")):
					os.remove(itemFilePath);
					log_result(fileName, itemFilePath, "INVALID_SHAREPOINT_NAME", "DELETE", "The path {} is a DESKTOP.INI file and is going to be deleted".format(itemFilePath));
				else:
					log_result(fileName, itemFilePath, "INVALID_SHAREPOINT_NAME", "RENAME PROMPT", "");
					rename_file(itemFilePath);
				
def rename_file(oldPath):
	print("The following file needs to be renamed:");
	print(oldPath);
	#typewrite(oldPath);
	new_name = input();
	if(new_name):
		os.rename(oldPath, new_name);
		log_result("", oldPath, "RENAMED", new_name, "");
		return True;
	else:
		print("   SKIP   ");
		log_result("", oldPath, "", "SKIP", "");
		return False;

def opt2_check_similarity(filePath):
	filePathArray = filePath.split("~$");
	fullpath = filePathArray[0];
	itemName = filePathArray[1];

	#print("CHECK SIMILARITY ON: {}".format(fullpath))
	for filepathitem in os.listdir(fullpath):
		#print("CHECK: {} ".format(filepathitem));
		
		if(filepathitem.endswith(itemName)):
			if ("~$"+itemName) not in filepathitem:
				#print("SIMILARITY FOUND: {}".format(filepathitem))
				return True
	#print("NO SIMILARITY FOUND")
	return False
	
def opt2_check_tiny_file(filePath):
	
	if(os.path.getsize(filePath) < 1000):
		return True
	else:
		return False

def opt3_long_path(fileName):
	df = pandas.read_csv(fileName);

	df_filtered = df.query("ResultCode == 'PATH_LEN_GT_300'");

	for index, row in df_filtered.iterrows():
		itemFilePath = row['SourcePath'];
		itemName = row['SourceBasename'];
		itemFilePathLen = len(itemFilePath);
		
		# Check if File still exists
		if (validate_file(itemFilePath)):
			if(itemFilePathLen > 300):
				itemNameLen = len(itemName);

				excedingChars = abs(300 - itemFilePathLen);

				if(itemFilePathLen - len(itemName) > 299):
					log_result(fileName, itemFilePath, "PATH_LEN_GT_300", "NONE", "FIX PATH: {} | {} exceding chars.".format(itemFilePath, excedingChars));
				else:
					log_result(fileName, itemFilePath, "PATH_LEN_GT_300", "NONE", "FIX FILE: {} | {} exceding chars.".format(itemFilePath, excedingChars));
			else:
				log("WARN: The path {} is not PATH_LEN_GT_300".format(itemFilePath))
				log_result(fileName, itemFilePath, "PATH_LEN_GT_300", "NONE", "WARN: The path {} is not PATH_LEN_GT_300".format(itemFilePath));

def get_log_file():
	global log_file
	if log_file is None:
		log_file = open(LOG_NAME,'a');
	
	return log_file
	
def get_log_results_file():
	global log_results_file
	if log_results_file is None:
		log_results_file = open(LOG_RESULTS_NAME,'a');
	
	return log_results_file

def log(text):
	now = datetime.now();
	dt = now.strftime("%Y-%m-%d %H:%M:%S");
	get_log_file().write(dt + ' -- ' + text + '\n');
	get_log_file().flush();
	
def log_result(fileProcessing, path, state, result, message):
	now = datetime.now();
	dt = now.strftime("%Y-%m-%d %H:%M:%S");
	get_log_results_file().write(dt + '|' + fileProcessing + '|' + path + '|' + state + '|' + result + '|' + message + '\n');
	get_log_results_file().flush();

def close_log():
	log_file.close();
	
def close_log_results():
	log_results_file.close();

# ========= FUNCTIONS END ============ #

fileName = argv[1];

try:
	log('Starting SMU program...')

	# Validate if file exists
	if validate_file(fileName):
		print("File "+ fileName +" OK")

		with open(fileName, encoding="utf8") as file:
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

					if option == '1': ## OPTION Process Empty Files
						log('1')
						opt1_empty_files(fileName);
						again = False;

					elif option == '2': ## OPTION Process Invalid Sharepoint Names
						log('2')
						opt2_invalid_names(fileName);
						again = False
					elif option == '3': ## OPTION Process Long Paths (GT 300)
						log('3')
						opt3_long_path(fileName);
						again = False
					elif option == '5': ## OPTION Show results on screen
						log('5')
						fingerprint(results)
						again = False
					elif option == '4': ## OPTION Log results and exit
						log('4')
						opt4_log_results(fileName, results);
						break;
					elif option == '6': ## OPTION Only exit
						log('6')
						break;
						
					print("Processing {} option finished".format(option))

					if again :
						option = input("\nSorry... Which option? ")
					else:
						again = True
						option = input("\nWe came back to the start. Which option now? ")

					# Program end
				
			else:
				print("Invalid file layout")
	else:
		print("File \""+ fileName + "\" not exists")

except Exception as e:
	logging.error(traceback.format_exc())

finally:
	log('Closing program...');
	close_log();
	close_log_results();
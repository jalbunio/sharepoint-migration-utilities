import os;
from sys import argv;

RESULT_FILE_NAME = 'scanlog_unified.csv'
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
#=========== FUNCTIONS START ==============#

def processFile(filePath, item):
	fullPath = os.path.join(filePath, item);

	if validateFile(fullPath):
		print("Processing \"{}\" ...".format(fullPath));
		unifyFile(fullPath);
	else:
		print("Ignoring \"{}\" ...".format(item));

def unifyFile(fullPath):
	with open(RESULT_FILE_NAME, "a") as resultFile:
		with open(fullPath, "r") as logFile:
			lines = logFile.readlines();
			
			for line in lines:
				if not line.startswith('\ufeff'):
					resultFile.write(line);				

def validateFile(fullPath):
	with open(fullPath, "r") as logFile:
		lines = logFile.readlines();
		text = lines[0];

	if text.strip().replace('\"','').replace('\ufeff', '')==LAYOUT_REPORT.strip().replace('\"','').replace('\ufeff', ''):
		return True
	else:
		return False

def initializeResultFile():
	with open(RESULT_FILE_NAME, "w") as resultFile:
		resultFile.write(LAYOUT_REPORT+"\n");	

#=========== FUNCTIONS END ================#

if len(argv) > 1 and argv[1] is not None:
	filePath = argv[1];
else:
	filePath = os.getcwd();

''' Validar diretorio '''
if os.path.isdir(filePath):
	initializeResultFile();
	print("Looking for result files in \"{}\" ...".format(filePath));

	for item in os.listdir(filePath):
		if item.endswith('.csv') and item != RESULT_FILE_NAME:
			processFile(filePath, item);
		else:
			print("Ignoring \"{}\" ...".format(item));
else:
	print("Sorry! The path \"{}\" is not a directory...".format(filePath));
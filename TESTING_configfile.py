#! /usr/bin/python

import argparse
import configparser
import os.path
import sys

debug = False

programName = "configfile.py"
programDescription = "Testing for a configfile"

nest_username = ""
nest_pw = ""

db_addr = ""
db_username = ""
db_pw = ""
db_database = ""

###########
# GET ARGS
##########
def getArgs():
	parser = argparse.ArgumentParser(prog=programName, description=programDescription)
	parser.add_argument("-c","--configfile",help="Configuration file path",required=True)
	parser.add_argument("-d","--debug",help="Debug Mode",required=False,action="store_true")
	return parser.parse_args()

def getConfig():
	global nest_username
	global nest_pw
	global db_addr
	global db_username
	global db_pw
	global db_database
	
	#if (os.path.isfile(args.configfile))
	fileexists = os.path.isfile(args.configfile)
	
	if (not os.path.isfile(args.configfile)):
		sys.exit("Error: Argument input config file '" + args.configfile + "' does not exist.  Exiting script...")
		
	c = configparser.RawConfigParser()
	c.read(args.configfile)
	
	nest_username = c.get('nest', 'username').strip('"')
	nest_pw = c.get('nest', 'passwd').strip('"')
	
	db_addr = c.get('database', 'address').strip('"')
	db_username = c.get('database', 'username').strip('"')
	db_pw = c.get('database', 'passwd').strip('"')
	db_database = c.get('database', 'database').strip('"')

	
def main(args):
	global debug
	if(args.debug):
		debug = True
	
	getConfig()
	
	print(nest_username)
	print(nest_pw)
	print(db_addr)
	print(db_username)
	print(db_pw)
	print(db_database)
		
	
	
	
	print("done")
	
if __name__ == '__main__':
	args = getArgs()
	
	main(args)
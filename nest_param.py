#! /usr/bin/python
#########################################################
#         Nest MySQL Data Logger Input CMDLine parsing  #
#########################################################
# Derek Rowland - 2017                                  #
# derek.a.rowland@gmail.com                             #
#                                                       #
# Based on project:                                     #
#   nest_data_logger.py                                 #
#   https://zpriddy.com/posts/python-nest-data-logger/  #
# Zachary Priddy - 2015                                 #
# me@zpriddy.com                                        #
#                                                       #
# Features:                                             #
#                                                       #
#                                                       #
#                                                       #
#########################################################
#########################################################

#notes:
# run time doesn't account for heater state (which I added to code)

#########
#IMPORTS
#########
import argparse


#########
#VARS
#########
programName="nest_param.py"
programDescription="This program calls the nest API to record data every two minutes to log nest statistics to mysql server"

nest_username = ""
nest_pw = ""

db_addr = ""
dp_port = ""
db_username = ""
db_pw = ""
db_database = ""
##################################################
#FUNCTIONS
##################################################

###########
# GET ARGS
##########
def getArgs():
	parser = argparse.ArgumentParser(prog=programName, description=programDescription)
	parser.add_argument("-nu","--nest_user",help="Nest API username",required=True)
	parser.add_argument("-np","--nest_pw",help="Nest API password",required=True)
	parser.add_argument("-da","--db_addr",help="Database IP Address",required=True)
	parser.add_argument("-dp","--db_port",help="Database Port",required=False,default="3306")
	parser.add_argument("-du","--db_user",help="Database Username",required=True)
	parser.add_argument("-dw","--db_pass",help="Database Password",required=True)
	parser.add_argument("-ds","--db_sch",help="Database Schema",required=False,default="nest")
	parser.add_argument("-d","--debug",help="Debug Mode - One Time Run and Debug Info",required=False,action="store_true")
	parser.add_argument("-x","--deletelogs",help="Delete old log files",required=False,action="store_true",default=False)


	return parser.parse_args()

	###############################################
	# OTHER NOTES 
	# 
	# For groups of args [in this case one of the two is required]:
	# group = parser.add_mutually_exclusive_group(required=True)
	# group.add_argument("-a1", "--arg1", help="ARG HELP")
	# group.add_argument("-a2", "--arg2", help="ARG HELP")
	#
	# To make a bool thats true:
	# parser.add_argument("-a","--arg",help="ARG HELP", action="store_true")
	#
	###############################################

###########
# GET CONFIG FILE INFO
##########
def getConfig():
	global nest_username
	global nest_pw
	global db_addr
	global db_port
	global db_username
	global db_pw
	global db_database
	
	
	
	nest_username = args.nest_user
	nest_pw = args.nest_pw
	db_addr = args.db_addr
	db_port = args.db_port
	db_username = args.db_user
	db_pw = args.db_pass
	db_database = args.db_sch
	
	#db_addr = c.get('database', 'address').strip('"')
	#db_username = c.get('database', 'username').strip('"')
	#db_pw = c.get('database', 'passwd').strip('"')
	#db_database = c.get('database', 'database').strip('"')


#############
# MAIN
#############
def main(args):
	global debug
	global deletelogs
	
	if(args.debug):
		debug = True
		
	getConfig()
	
	print("Starting nest logging......")
	print("  Using: ")
	print("         Nest User:    " + nest_username)
	print("         Nest PW:      " + nest_pw)
	print("         DB Address:   " + db_addr)
	print("         DB Port:      " + db_port)
	print("         DB User:      " + db_username)
	print("         DB Passwd:    " + db_pw)
	print("         DB Schema:    " + db_database)

		
	#sys.exit("EXITING FOR TEST")
	


#############
# END OF MAIN
#############

#############
# USER CLASS
#############
class User:
	def __init__(self,username=None,password=None,filename=None):
		self.username = username
		self.password = password
		self.filename = filename








###########################
# PROG DECLARE
###########################
if __name__ == '__main__':
	args = getArgs()
	main(args)

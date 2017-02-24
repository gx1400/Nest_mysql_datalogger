#! /usr/bin/python
#########################################################
#           Nest MySQL Data Logger                      #
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
import nest
import utils
import pickle
from datetime import * 
import dateutil.parser
import threading

#for config parsing
import os.path
import sys
import configparser

#for deleting old log files
import time
import re

#for mysql socket
from mysql.connector import (connection)


#########
#VARS
#########
programName="nest_data_logger.py"
programDescription="This program calls the nest API to record data every two minutes to log nest statistics to mysql server"


debug = False
deletelogs = False

#store script folder location
dir_path = os.path.dirname(os.path.realpath(__file__))

away_temp = 0
second_timestamp = ''

nest_username = ""
nest_pw = ""

db_addr = ""
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
	parser.add_argument("-c","--configfile",help="Configuration file path",required=True)
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



def readUserFromFile(user,filename):
	print ("Read Account File")

def nestAuth(user):
	myNest = nest.Nest(user.username,user.password,cache_ttl=0)
	return myNest

def dataLoop(nest):
	global debug
	global second_timestamp
	global away_temp
	
	if(not debug):
		threading.Timer(120,dataLoop,args=[nest]).start() #120s
	print ("Running Data Loop...")

	dayLog = []
	
	#build log file name, this will change after midnight
	log_filename = os.path.join(dir_path,"logs",str(datetime.now().year) +'-' + str(datetime.now().month) + '-' + str(datetime.now().day) + '.log')
	print("Log file: " + log_filename)
	
	#check for log file directory
	#delete old log files if -x option was added
	deleteoldlogs(dir_path)	
	
	#try to open existing log files
	try:
		dayLog = pickle.load(open(log_filename, 'rb'))
		dayLogIndex = len(dayLog)
	except:
		print ("No Current Log File")
		dayLogIndex = 0 

	log = {}
		
	#execute nest API pull
	data = nest.devices[0]
	structure = nest.structures[0]
	
	#Start nest API parsing
	deviceData(data,log)
	sharedData(data, log)
	weatherData(data,log)
	structureData(structure,log)

	#current time stamp for logging later
	log['$timestamp'] = datetime.now().isoformat()

	#adjust target temp for heat/cool mode.  I don't use heat+cool
	if (log['target_type'] == "cool"):
		away_temp = log['away_temp_high']
	elif (log['target_type'] == "heat"):
		away_temp = log['away_temp_low']
	else:
		away_temp = 0
	print("Away temp, " + str(log['target_type']) + ": " + str(away_temp))
	
	#calculate 
	calcTotals(log,dayLog)

	
	#can remove this since cleaning up comments
	if(dayLogIndex != 0):
		dayLog.append(log)
	else:
		dayLog.append(log)

	# write information to log file using Pickle
	try:
		pickle.dump(dayLog,open(log_filename,'wb'))
	except:
		print ("Error Saving Log: ", log_filename)
	
	#write to MySQL
	logToMySQL(log)

	#print dayLog

def logToMySQL(log):

	# Open database connection
	cnx = connection.MySQLConnection(
		user=db_username, 
		password=db_pw, 
		host=db_addr, 
		database=db_database)
	
							  
	# prepare a cursor object using cursor() method
	cursor = cnx.cursor()

	#handle explicit string conversion upfront
	str_trans_time = str(log['trans_time'])						
	str_totalruntime = str(log['total_run_time']) 				
	str_leaf_temp = str(log['leaf_temp'])						
	str_target_type = str(log['target_type'])					
	str_totalruntime_away = str(log['total_run_time_away'])		
	str_outside_temperature = str(log['outside_temperature'])	
	str_ac_state = str(log['ac_state'])							
	str_timestamp = str(log['$timestamp'])						
	str_current_temperature = str(log['current_temperature'])	
	str_away = str(log['away'])									
	str_target_temp = str(log['target_temperature'])			
	str_totalruntime_home = str(log['total_run_time_home'])		
	str_fan_state = str(log['fan_state'])						
	str_total_trans_time = str(log['total_trans_time'])			
	str_humidity = str(log['humidity'])
	str_winddir = str(log['wind_dir'])
	str_windmph = str(log['wind_mph']) 
	str_condition = str(log['condition']) 
	str_heater_state = str(log['heat_state'])
	
	query = ("INSERT INTO nest.nest_log "
					"(trans_time, total_run_time, leaf_temp, target_type, total_run_time_away, "
					"outside_temperature, ac_state, time_stamp, current_temperature, away, "
					"target_temp, total_run_time_home, fan_state, total_trans_time, humidity, "
					"wind_dir, wind_mph, weather_Condition, heater_state"
					") "
					"VALUES "
					"(%s, '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', %s, '%s', '%s', %s, '%s', "
					"'%s', '%s', '%s', '%s', %s )" 
					% (str_trans_time, str_totalruntime, str_leaf_temp, str_target_type, 
					str_totalruntime_away, str_outside_temperature, str_ac_state, 
					str_timestamp, str_current_temperature, str_away, str_target_temp, 
					str_totalruntime_home, str_fan_state, str_total_trans_time, str_humidity,
					str_winddir, str_windmph, str_condition, str_heater_state)
				)
	
	print(query)
	
	cursor.execute(query)

	cnx.commit()
	cursor.close()
	cnx.close
	
def deviceData(data,log):
	
	deviceData = data._device
	log['leaf_temp'] = utils.c_to_f(deviceData['leaf_threshold_cool'])
	#away_temp = utils.c_to_f(deviceData['away_temperature_high'])
	log['away_temp_high'] = utils.c_to_f(deviceData['away_temperature_high'])
	log['away_temp_low'] = utils.c_to_f(deviceData['away_temperature_low'])
	log['$timestamp'] = datetime.fromtimestamp(deviceData['$timestamp']/1000).isoformat()
	log['humidity'] = deviceData['current_humidity']
	#print('\n'.join(str(p) for p in deviceData))

def sharedData(data,log):
	sharedData = data._shared
	log['target_type'] = sharedData['target_temperature_type']
	log['fan_state'] = sharedData['hvac_fan_state']
	log['target_temperature'] = utils.c_to_f(sharedData['target_temperature'])
	log['current_temperature'] = utils.c_to_f(sharedData['current_temperature'])
	log['ac_state'] = sharedData['hvac_ac_state']
	log['heat_state'] = sharedData['hvac_heater_state']
	#print('\n'.join(str(p) for p in sharedData))
	
def weatherData(data,log):
	weatherData = data.weather._current
	log['outside_temperature'] = weatherData['temp_f']
	log['wind_dir'] = weatherData['wind_dir']
	log['wind_mph'] = weatherData['wind_mph']
	log['condition'] = weatherData['condition']
	#print('\n'.join(str(p) for p in weatherData))

def structureData(structure,log):
	global second_timestamp
	structureData = structure._structure
	second_timestamp = datetime.fromtimestamp(structureData['$timestamp']/1000).isoformat()
	log['away'] = structureData['away']
	#print('\n'.join(str(p) for p in structureData))

def calcTotals(log, dayLog):
	global away_temp
	dayLogLen = len(dayLog)
	
	#this would be first time script is running (so no log file) or 
	# it's a new day, so new log file
	if(dayLogLen == 0):
		log['total_run_time'] = 0
		log['total_run_time_home'] = 0
		log['total_run_time_away'] = 0
		log['total_trans_time'] = 0
		log['trans_time'] = False
	
	else:
		index = dayLogLen - 1 #list(dayLog)[dayLogLen-1]
		
		#if the ac AND heater aren't running, AND they weren't running before 
		# then copy values from last log
		if(log['ac_state'] == False and dayLog[index]['ac_state'] == False and log['heat_state'] == False and dayLog[index]['heat_state'] == False):
			log['total_run_time'] = dayLog[index]['total_run_time']
			log['total_run_time_home'] = dayLog[index]['total_run_time_home']
			log['total_run_time_away'] = dayLog[index]['total_run_time_away']
			log['trans_time'] = False
			log['total_trans_time'] = dayLog[index]['total_trans_time']
		
		#start to handle situations where heater OR AC are on....
		# 
		else:
			#calculate time difference
			then = dateutil.parser.parse(dayLog[index]['$timestamp'])
			now = dateutil.parser.parse(log['$timestamp'])
			diff = now - then
			diff = diff.total_seconds()/60
			log['total_run_time'] = dayLog[index]['total_run_time'] + diff

			
			
			#if away, add to away runtime
			if(log['away']):
				print ("CURRENTLY AWAY")
				log['total_run_time_away'] = dayLog[index]['total_run_time_away'] + diff
				log['total_run_time_home'] = dayLog[index]['total_run_time_home']
				log['target_temperature'] = away_temp
			#if home (not away), add to home runtime
			elif(not log['away']):
				log['total_run_time_home'] = dayLog[index]['total_run_time_home'] + diff
				log['total_run_time_away'] = dayLog[index]['total_run_time_away']
			
			
			
			#the following section is used to track equipment run time when transitioning from
			#  away to home.  essentially 'trans_time' is 'latched' until both the AC and heater
			#  stop running, after the transition back to being home
			#
			# log['away'] is "current" state
			# dayLog[index]['away'] is "previous" state
			
			#if we were away but we are now not away, and the ac is on, then add to transition time
			#  latch us into an 'transition' state with 'trans_time'
			if(log['away'] == False and dayLog[index]['away'] == True and log['ac_state'] == True):
				log['trans_time'] = True
				log['total_trans_time'] = dayLog[index]['total_trans_time'] + diff
			
			#if we were away but we are now not away, and the heater is on, then add to transition time
			#  latch us into an 'transition' state with 'trans_time'
			elif(log['away'] == False and dayLog[index]['away'] == True and log['heat_state'] == True):
				log['trans_time'] = True
				log['total_trans_time'] = dayLog[index]['total_trans_time'] + diff
			
			#if we were in a 'trans_time' state, and we're not away, then stay in trans state
			#  NOT SURE HOW THIS IS UNLATCHED?!
			#elif(log['away'] == False and dayLog[index]['away'] == False and dayLog[index]['trans_time'] == True and (log['heat_state'] == True or log['ac_state'] == True)):
			#
			#testing adding 'heat state true' and 'ac state true' to trans time latch, so if we're home and have
			# been home, and are in a transition state, AND Ac or heater are STILL running, then keep trans_time
			# latched and count up.
			elif(log['away'] == False and dayLog[index]['away'] == False and dayLog[index]['trans_time'] == True and (log['heat_state'] == True or log['ac_state'] == True)):
				log['trans_time'] = True
				log['total_trans_time'] = dayLog[index]['total_trans_time'] + diff
			
			# not in a transition, so unlatch and hold trans _time accumulation
			else:
				log['trans_time'] = False
				log['total_trans_time'] = dayLog[index]['total_trans_time']

	if(log['away']):
		print ("CURRENTLY AWAY")
		log['target_temperature'] = away_temp



def deleteoldlogs(dir_path):
	
	logpath = os.path.join(dir_path, "logs")
	
	#if log folder doesn't exist yet, create it
	if (not os.path.exists(logpath)):
		os.makedirs(logpath)
		return
	
	#change this to keep more older files
	daystodelete = 2
	
	now = time.time()
	
	#find files that fit the log file format, so we don't
	#accidentally delete files
	files = [f for f in os.listdir(logpath) if re.match(r'[0-9]+\-[0-9]+\-[0-9]+\.log', f)]
	
	if deletelogs:
		for f in files:
			f = os.path.join(logpath, f)
			if os.stat(f).st_mtime < now - daystodelete * 86400:
				print("File being deleted: " + f)
				if os.path.isfile(f):
					os.remove(f)

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
	print("         Config file:  " + args.configfile)
	print("         Nest User:    " + nest_username)
	print("         Nest PW:      " + nest_pw)
	print("         DB Address:   " + db_addr)
	print("         DB User:      " + db_username)
	print("         DB Passwd:    " + db_pw)
	print("         DB Schema:    " + db_database)
	
	# set global setting for deleting old log files
	deletelogs = args.deletelogs
		
	#sys.exit("EXITING FOR TEST")
	
	nestUser = User(username=nest_username,password=nest_pw) 
	myNest = nestAuth(nestUser)


	dataLoop(myNest)



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
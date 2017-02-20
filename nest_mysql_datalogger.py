#! /usr/bin/python
#########################################################
#			Nest MySQL Data Logger						#
#########################################################
# Derek Rowland - 2017									#
# derek.a.rowland@gmail.com								#
#														#
# Based on project:										#
#	nest_data_logger.py									#
#	https://zpriddy.com/posts/python-nest-data-logger/	#
# Zachary Priddy - 2015 								#
# me@zpriddy.com 										#
#														#
# Notes: 												#
#	- Commented out pygal and file logging code			#
#########################################################
#########################################################

#########################################################
#########################################################
#														#
#	MySQL Database Creation Statement					#
#														#
#########################################################
#CREATE DATABASE `nest` /*!40100 DEFAULT CHARACTER SET utf8 */;
#
#########################################################
#########################################################


#########################################################
#########################################################
#														#
#	MySQL Table Creation Statement						#
#														#
#########################################################
#
#CREATE TABLE `nest_log` (
#  `index` int(11) NOT NULL AUTO_INCREMENT,
#  `trans_time` bit(1) DEFAULT NULL,
#  `total_run_time` double DEFAULT NULL,
#  `leaf_temp` double DEFAULT NULL,
#  `target_type` varchar(45) DEFAULT NULL,
#  `total_run_time_away` double DEFAULT NULL,
#  `outside_temperature` double DEFAULT NULL,
#  `ac_state` bit(1) DEFAULT NULL,
#  `time_stamp` timestamp NULL DEFAULT NULL,
#  `current_temperature` double DEFAULT NULL,
#  `away` bit(1) DEFAULT NULL,
#  `target_temp` double DEFAULT NULL,
#  `total_run_time_home` double DEFAULT NULL,
#  `fan_state` bit(1) DEFAULT NULL,
#  `total_trans_time` double DEFAULT NULL,
#  `humidity` double DEFAULT NULL,
#  `wind_dir` varchar(10) DEFAULT NULL,
#  `wind_mph` double DEFAULT NULL,
#  `weather_condition` varchar(45) DEFAULT NULL,
#  PRIMARY KEY (`index`)
#) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
#
#########################################################
#########################################################


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
import pygal
#from bokeh.plotting import *
#import numpy as np
#import pandas as pd
#from bokeh.charts import TimeSeries, show, output_file
#from collections import OrderedDict

from mysql.connector import (connection)


#########
#VARS
#########
programName="nest_mysql_datalogger.py"
programDescription="This program calls the nest API to record data every two minutes to render a daily graph"


debug = False
away_temp = 0
second_timestamp = ''


##################################################
#FUNCTIONS
##################################################

###########
# GET ARGS
##########
def getArgs():
	parser = argparse.ArgumentParser(prog=programName, description=programDescription)
	parser.add_argument("-u","--username",help="Nest Account Username",required=True)
	parser.add_argument("-p","--password",help="Nest Account Password",required=True)
	#parser.add_argument("-f","--accountfile",help="Nest Account Ifno Saved In File",required=False) #To Add In Later
	parser.add_argument("-d","--debug",help="Debug Mode - One Time Run and Debug Info",required=False,action="store_true")


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

##############
# END OF ARGS
##############


def readUserFromFile(user,filename):
	print ("Read Account File")

def nestAuth(user):
	myNest = nest.Nest(user.username,user.password,cache_ttl=0)
	return myNest

def dataLoop(nest):
	global debug
	global second_timestamp
	if(not debug):
		threading.Timer(120,dataLoop,args=[nest]).start() #120s
	print ("Running Data Loop...")

	dayLog = []
	#log_filename = 'logs/' + str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day) + '.log'
	try:
		#dayLog = pickle.load(open(log_filename, 'rb'))
		dayLogIndex = len(dayLog)
	except:
		print ("No Current Log File")
		dayLogIndex = 0 


	log = {}
	data = nest.devices[0]
	structure = nest.structures[0]
	deviceData(data,log)
	sharedData(data, log)
	weatherData(data,log)

	structureData(structure,log)

	log['$timestamp'] = datetime.now().isoformat()

	calcTotals(log,dayLog)

	

	if(dayLogIndex != 0):
		#if(log['$timestamp'] != dayLog[dayLogIndex-1]['$timestamp']):
		dayLog.append(log)
		#else:
		#	log['$timestamp'] = second_timestamp
		#	if(log['$timestamp'] != dayLog[dayLogIndex-1]['$timestamp']):
		#		dayLog.append(log)
		#	else:
		#		print ("No chnage in timestamp recieved.. No new data logged.")
	else:
		dayLog.append(log)

	#try:
	#	pickle.dump(dayLog,open(log_filename,'wb'))
	#except:
	#	print ("Error Saving Log: ", log_filename)

	for x in range(0,len(dayLog)):
		print (dayLog[x])

	#generateGraph(dayLog)

	logToMySQL(log)

	#print dayLog

def logToMySQL(log):
	# Open database connection
	cnx = connection.MySQLConnection(user='root', password='hellomysql',
							     host='127.0.0.1',
							     database='nest')
							  
	# prepare a cursor object using cursor() method
	#cursor = db.cursor()
	cursor = cnx.cursor()

	# execute SQL query using execute() method.
	#cursor.execute("SELECT VERSION()")
	#query = ("SELECT VERSION()")
		
	str_trans_time = str(log['trans_time'])						#
	str_totalruntime = str(log['total_run_time']) 				#
	str_leaf_temp = str(log['leaf_temp'])						
	str_target_type = str(log['target_type'])					
	str_totalruntime_away = str(log['total_run_time_away'])		#
	str_outside_temperature = str(log['outside_temperature'])	#
	str_ac_state = str(log['ac_state'])							
	str_timestamp = str(log['$timestamp'])						#
	str_current_temperature = str(log['current_temperature'])	
	str_away = str(log['away'])									
	str_target_temp = str(log['target_temperature'])			
	str_totalruntime_home = str(log['total_run_time_home'])		#
	str_fan_state = str(log['fan_state'])						
	str_total_trans_time = str(log['total_trans_time'])			#
	str_humidity = str(log['humidity'])
	str_winddir = str(log['wind_dir'])
	str_windmph = str(log['wind_mph']) 
	str_condition = str(log['condition']) 
	
	
	query = ("INSERT INTO nest.nest_log "
					"(trans_time, total_run_time, leaf_temp, target_type, total_run_time_away, "
					"outside_temperature, ac_state, time_stamp, current_temperature, away, "
					"target_temp, total_run_time_home, fan_state, total_trans_time, humidity, "
					"wind_dir, wind_mph, weather_Condition"
					") "
					"VALUES "
					"(%s, '%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', %s, '%s', '%s', %s, '%s', "
					"'%s', '%s', '%s', '%s' )" 
					% (str_trans_time, str_totalruntime, str_leaf_temp, str_target_type, 
					str_totalruntime_away, str_outside_temperature, str_ac_state, 
					str_timestamp, str_current_temperature, str_away, str_target_temp, 
					str_totalruntime_home, str_fan_state, str_total_trans_time, str_humidity,
					str_winddir, str_windmph, str_condition)
				)
	
	print(query)
	
	#query = ("INSERT INTO nest.nest_log "
	#		"(outside_temperature, time_stamp) "
	#		"VALUES "
	#		"('" + str_outside_temperature + "', '" + str_timestamp + "')")

	#print(query)
	
	# Fetch a single row using fetchone() method.
	#data = cursor.fetchone()
	cursor.execute(query)

	cnx.commit()
	cursor.close()
	cnx.close
	
def deviceData(data,log):
	global away_temp
	deviceData = data._device
	log['leaf_temp'] = utils.c_to_f(deviceData['leaf_threshold_cool'])
	away_temp = utils.c_to_f(deviceData['away_temperature_high'])
	log['$timestamp'] = datetime.fromtimestamp(deviceData['$timestamp']/1000).isoformat()
	log['humidity'] = deviceData['current_humidity']
	

def sharedData(data,log):
	sharedData = data._shared
	log['target_type'] = sharedData['target_temperature_type']
	log['fan_state'] = sharedData['hvac_fan_state']
	log['target_temperature'] = utils.c_to_f(sharedData['target_temperature'])
	log['current_temperature'] = utils.c_to_f(sharedData['current_temperature'])
	log['ac_state'] = sharedData['hvac_ac_state']

	
def weatherData(data,log):
	weatherData = data.weather._current
	log['outside_temperature'] = weatherData['temp_f']
	log['wind_dir'] = weatherData['wind_dir']
	log['wind_mph'] = weatherData['wind_mph']
	log['condition'] = weatherData['condition']
	

def structureData(structure,log):
	global second_timestamp
	structureData = structure._structure
	second_timestamp = datetime.fromtimestamp(structureData['$timestamp']/1000).isoformat()
	log['away'] = structureData['away']

def calcTotals(log, dayLog):
	global away_temp
	dayLogLen = len(dayLog)
	if(dayLogLen == 0):
		log['total_run_time'] = 0
		log['total_run_time_home'] = 0
		log['total_run_time_away'] = 0
		log['total_trans_time'] = 0
		log['trans_time'] = False
	else:
		index = dayLogLen - 1 #list(dayLog)[dayLogLen-1]
		if(log['ac_state'] == False and dayLog[index]['ac_state'] == False):
			log['total_run_time'] = dayLog[index]['total_run_time']
			log['total_run_time_home'] = dayLog[index]['total_run_time_home']
			log['total_run_time_away'] = dayLog[index]['total_run_time_away']
			log['trans_time'] = False
			log['total_trans_time'] = dayLog[index]['total_trans_time']
		#elif(log['ac_state'] == True and dayLog[index]['ac_state'] == False):
			#log['total_run_time'] = dayLog[index]['total_run_time']
			#log['total_run_time_home'] = dayLog[index]['total_run_time_home']
			#log['total_run_time_away'] = dayLog[index]['total_run_time_away']
			#log['trans_time'] = False
			#log['total_trans_time'] = dayLog[index]['total_trans_time']
		else:
			then = dateutil.parser.parse(dayLog[index]['$timestamp'])
			now = dateutil.parser.parse(log['$timestamp'])
			diff = now - then
			diff = diff.total_seconds()/60
			log['total_run_time'] = dayLog[index]['total_run_time'] + diff

			if(log['away']):
				print ("CURRENTLY AWAY")
				log['total_run_time_away'] = dayLog[index]['total_run_time_away'] + diff
				log['total_run_time_home'] = dayLog[index]['total_run_time_home']
				log['target_temperature'] = away_temp
			elif(not log['away']):
				log['total_run_time_home'] = dayLog[index]['total_run_time_home'] + diff
				log['total_run_time_away'] = dayLog[index]['total_run_time_away']

			if(log['away'] == False and dayLog[index]['away'] == True and log['ac_state'] == True):
				log['trans_time'] = True
				log['total_trans_time'] = dayLog[index]['total_trans_time'] + diff
			elif(log['away'] == False and dayLog[index]['away'] == False and dayLog[index]['trans_time'] == True):
				log['trans_time'] = True
				log['total_trans_time'] = dayLog[index]['total_trans_time'] + diff
			else:
				log['trans_time'] = False
				log['total_trans_time'] = dayLog[index]['total_trans_time']

	if(log['away']):
		print ("CURRENTLY AWAY")
		log['target_temperature'] = away_temp




def generateGraph(dayLog):

	timestamps = []
	total_run_time = []
	total_run_time_home = []
	total_run_time_away = []
	total_trans_time = []
	target_temperature = []
	current_temperature = []
	outside_temperature = []

	for log in dayLog:
		timestamps.append(log['$timestamp'])
		total_run_time.append(log['total_run_time'])
		total_run_time_home.append(log['total_run_time_home'])
		total_run_time_away.append(log['total_run_time_away'])
		total_trans_time.append(log['total_trans_time'])
		target_temperature.append(log['target_temperature'])
		current_temperature.append(log['current_temperature'])
		outside_temperature.append(log['outside_temperature'])

	##line_chart = pygal.Line(x_label_rotation=20,x_labels_major_every=30,show_minor_x_labels=False,dots_size=.2,width=1200,tooltip_border_radius=2)
	##line_chart.title = 'Daily Nest Usage'
	##line_chart.x_labels = timestamps
	##line_chart.add('Total Run Time', total_run_time)
	##line_chart.add('Home Run Time', total_run_time_home)
	##line_chart.add('Away Run Time', total_run_time_away)
	##line_chart.add('Trans Run Time', total_trans_time)
	##line_chart.add('Target Temperature', target_temperature)
	##line_chart.add('Inside Temperature', current_temperature)
	##line_chart.add('Outside Temperature', outside_temperature)

	##line_chart.render_to_file('daily.svg')  


	#output_file("bokeh.html", title="Nest Graph")
	#dates =  np.array(timestamps,dtype='datetime64')
	#inside_temp = np.array(current_temperature)
	#target_temp = np.array(target_temperature)
	#outside_temp = np.array(outside_temperature)
	#p = figure(width=800, height=350, x_axis_type="datetime")
	#p = figure(title="Nest Graph", x_axis_label='Date', y_axis_label='Inside Temp')
	#p.line(dates, inside_temp, legend="Temp.", line_width=2)
	#p.circle(dates, inside_temp, legend="y=x", fill_color="white", size=8)
	#p.line(dates, outside_temp, legend="Outside.", line_width=2,line_color="orange", line_dash="4 4")
	#p.line(dates, target_temp, legend="Target.", line_width=2,line_color="red", line_dash="2 2")
	#show(p)

	#TOOLS="resize,pan,wheel_zoom,box_zoom,reset,previewsave"
	#timestamps = []
	#for log in dayLog:
	#	print log['$timestamp']

	#xyvalues = OrderedDict(
	#	INSIDE=inside_temp,
	#	OUTSIDE=outside_temp,
	#	TARGET=target_temp,
	#	DATE=dates
	#	)
	#ts = TimeSeries(
    #xyvalues, index='DATE', legend=True,
    #title="Temperature", tools=TOOLS, ylabel='Degrees F',palette=['red','blue','purple'])
	#ts2 = TimeSeries(
	#xyvalues, index='DATE', legend=True,
	#title="Temperature", tools=TOOLS, ylabel='Degrees F',palette=['red','blue','purple'])

	#p = gridchart([ts,ts2])

	#show(p)



#############
# MAIN
#############
def main(args):
	global debug
	if(args.debug):
		debug = True
	nestUser = User(username=args.username,password=args.password) #,filename=args.accountfile)
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
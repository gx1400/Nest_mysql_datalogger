#! /usr/bin/python

import os
import os.path
import time
import sys
import re


def deleteoldlogs():
	dir_path = os.path.dirname(os.path.realpath(__file__))
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
	

def main():
	deleteoldlogs()

if __name__ == '__main__':
	main()
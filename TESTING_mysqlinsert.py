#!/usr/bin/python

from mysql.connector import (connection)

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
query = ("INSERT INTO nest.testinsert "
		 "(ID, Name) "
		 "VALUES (1,'hello')")

# Fetch a single row using fetchone() method.
#data = cursor.fetchone()
cursor.execute(query)

cnx.commit()
cursor.close()

#print "Database version : %s " % data

# disconnect from server
#db.close()
cnx.close
import mbed_connector_api 				# mbed Device Connector library
import pybars 							# use to fill in handlebar templates
from   flask 			import Flask	# framework for hosting webpages
from   flask_socketio 	import SocketIO, emit,send,join_room, leave_room  
from   base64 			import standard_b64decode as b64decode
import os
import sys
import time
import MySQLdb as mdb
import Tkinter
from Tkinter import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

if 'ACCESS_KEY' in os.environ.keys():
	token = os.environ['ACCESS_KEY'] # get access key from environment variable
else:
	token = "OVei3PnFHGuoLvfMwpT5kngqLMnGGwLFm0yh5AyEER6LwRLVM9UMVmCSazTrjtGjfisQTzM9MBxkKM8ZVnQB38Xog41VtDcQYDAL" # replace with your API token

connector = mbed_connector_api.connector(token)
con = mdb.connect('localhost', 'root', '')      # connect to mysql
cur = con.cursor()                              # get the module of cursor



if __name__ == "__main__":
	# create database TempHumTable if it not exists
	cur.execute("create database if not exists temperature")
	# select the database TempHumTable
	cur.execute("use tempereture")
	# create table temp for storing the temparature data if it not exists
	cur.execute("create table if not exists temp(time TIME, temperature FLOAT(4,2), date DATE)")
	# # clean the temp & hum table everyday
	# curdate = time.strftime('%y:%m:%d')
	# cur.execute("delete from temp where date < %s", [curdate])
	# commit update to the database
	con.commit()
	print 'init database successfully!'
	

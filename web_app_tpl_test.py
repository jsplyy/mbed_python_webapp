import mbed_connector_api 				# mbed Device Connector library
import pybars 							# use to fill in handlebar templates
from   flask 			import Flask,request,render_template,Response	# framework for hosting webpages
from   flask_socketio 	import SocketIO, emit,send,join_room, leave_room  
from   base64 			import standard_b64decode as b64decode
import os
import random
import Queue
import json
import base64
import time

app = Flask(__name__)
socketio = SocketIO(app,async_mode='threading')

@app.route('/')
def index():
	return render_template("tpl_temp_resources.html")

@app.route('/mcu_temp')
def mcu_temp():
	return render_template("mcu_temp.html")

if __name__ == "__main__":

	socketio.run(app,host='0.0.0.0', port=81,debug=True)


import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

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
import MySQLdb as mdb
import time
import random
import datetime

app = Flask(__name__)
socketio = SocketIO(app,async_mode='threading')
queueTemp = Queue.Queue(maxsize = 30)
tempHighDic = {0:31, 1:29, 2:30, 3: 30, 4: 32, 5:32, 6: 33, 7:35, 8:36,9:34,10:38,11:36,12:39, 13:41, 14:38, 15:36,16:36,17:33,18:35, 19: 32,20:33,21:34,22:30,23:32 }
tempLowDic = {0:28, 1:27, 2:29, 3: 28, 4: 30, 5:27, 6: 29, 7:30, 8:33,9:31,10:36,11:35,12:38, 13:38, 14:37, 15:33,16:34,17:30,18:32, 19: 29,20:30,21:32,22:30,23:29 }
tempDisc={}
hoursTemp = {}


if 'ACCESS_KEY' in os.environ.keys():
	token = os.environ['ACCESS_KEY'] # get access key from environment variable
else:
	token = "4SMf3bbEWuzD8tGxM7Kg9LQr4RZY7xpEPgbHde5AKGFd63CHvNajtDN3PoACybLLqce1dwa9kld2ketBUpqwvZZG41SqPXw7Mtnr" # replace with your API token

connector = mbed_connector_api.connector(token)
connector.putCallback("http://mbed.iotcent.org:81/data")
print connector.getCallback().result
con = mdb.connect('localhost', 'root', '')      # connect to mysql
cur = con.cursor()                              # get the module of cursor

@app.route('/')
def index():
	epList = connector.getEndpoints().result
	print epList
	return render_template("index.html",epList=epList,number=range(len(epList)))

@app.route('/resources',methods=['GET'])
def resources():
	epResources = connector.getResources(request.args.get("pointid")).result
	number = range(len(epResources))
	return render_template("tpl_resources.html",pointid=request.args.get("pointid"),epResources=epResources,number=number)

@app.route('/get_blink_resource',methods=['GET'])
def get_blink_resource():
	epBlinkResource = connector.postResource(request.args.get("pointid"),request.args.get("blinkid"),"flash")
	data = json.loads(epBlinkResource.raw_data)	
	res_id = data['async-response-id']
	while res_id not in tempDisc.keys():
		None
	blinkValue = tempDisc[res_id]
	del tempDisc[res_id]
	return render_template("tpl_blink_resources.html")

@app.route('/get_button_resource',methods=['GET'])
def get_button_resource():
	epButtonResource = connector.getResourceValue(request.args.get("pointid"),request.args.get("buttonid"))
	data = json.loads(epButtonResource.raw_data)
	res_id = data['async-response-id']
	while res_id not in tempDisc.keys():
		None
	buttonNumber = tempDisc[res_id]
	del tempDisc[res_id]
	return render_template("tpl_btn_resources.html",cntNumber=buttonNumber,pointid=request.args.get("pointid"))

# ble uart 
@app.route('/get_ble_resource',methods=['GET'])
def get_ble_resource():
	epBleResource = connector.postResource(request.args.get("pointid"),request.args.get("bleid"))
	data = json.loads(epBleResource.raw_data)
	res_id = data['async-response-id']
	while res_id not in tempDisc.keys():
		None
	bleContent = tempDisc[res_id]
	del tempDisc[res_id]
	return render_template("tpl_ble_uart_resources.html",bleContent=bleContent,pointid=request.args.get("pointid"),bleid=request.args.get("bleid"))

@app.route('/get_acce_resource',methods=['GET'])
def get_acce_resource():
	epAcceResource = connector.postResource(request.args.get("pointid"),request.args.get("angleid"))
	data = json.loads(epAcceResource.raw_data)
	res_id = data['async-response-id']
	while res_id not in tempDisc.keys():
		None
	acceAngle = tempDisc[res_id]
	acceAngle = int(acceAngle)
	del tempDisc[res_id]
	return render_template("tpl_acce_resources.html",acceAngle=acceAngle,pointid=request.args.get("pointid"),angleid=request.args.get("angleid"))


@app.route('/get_pattern_resource',methods=['GET'])
def get_pattern_resource():
	if(request.args.get("value")!='1'):
		epPatternResource = connector.putResourceValue(request.args.get("pointid"),request.args.get("patternid"),request.args.get("value"))
		data = json.loads(epPatternResource.raw_data)
		res_id = data['async-response-id']
		while res_id not in tempDisc.keys():
			None
		patternValue = tempDisc[res_id]
		del tempDisc[res_id]
	epPatternResource = connector.getResourceValue(request.args.get("pointid"),request.args.get("patternid"))
	data = json.loads(epPatternResource.raw_data)
	res_id = data['async-response-id']
	while res_id not in tempDisc.keys():
		None
	patternValue = tempDisc[res_id]
	del tempDisc[res_id]
	
	return render_template("tpl_pattern_resources.html",patternContent=patternValue,pointid=request.args.get("pointid"),patternid=request.args.get("patternid"))

@app.route('/get_temp_resource', methods=['GET'])
def get_temp_resource():
	tempHour=[]; tempHigh=[]; tempLow=[]
	now = datetime.datetime.now()
	print now.hour
	for i in range(0,24)[::-1]:

		hours = now.hour + i - 23;
		if (hours<0):
			hours = hours + 24;
		tempHour.append(hours) 
		tempHigh.append(tempHighDic[hours])   
		tempLow.append(tempLowDic[hours])

	hoursTemp['hours'] = tempHour[::-1]
	hoursTemp['tempHigh'] = tempHigh[::-1]
	hoursTemp['tempLow'] = tempLow[::-1]	
	return render_template("tpl_temp_resources.html",pointid=request.args.get("pointid"),tempid=request.args.get("patternid"),tempData=hoursTemp);

@app.route('/mcu_temp', methods=['GET'])
def get_mcu_temp():
	pointid = "c9814c70-0944-4e03-a306-e4af7a7c579b"
	tempid = "/3205/0/3206"
	tempResource = connector.postResource(pointid,tempid)
	data = json.loads(tempResource.raw_data)
	res_id = data['async-response-id']
	while res_id not in tempDisc.keys():
		None
	tempValue = tempDisc[res_id]
	tempValue = int(tempValue)
	del tempDisc[res_id]
	
	#udpate
	now = datetime.datetime.now()
	hours = now.hour
	tempHighDic[hours] = tempValue
	tempLowDic[hours] = tempValue - random.randint(0,4)

	return Response(status=200)

@app.route('/mcu_temp_weekly', methods=['GET'])
def get_mcu_temp_weekly():
	return render_template('tpl_temp_resources_weekly.html')

@app.route('/mcu_temp/random', methods=['GET'])
def get_temp():
	if(request.args.get("data")=='2'):

		return str(random.randint(34,40))

@app.route('/temp', methods=['GET'])
def get_tem():
	return str(queueTemp.get())

@app.route('/test', methods=['GET'])
def get_test():
	if(request.args.get("temp")!='0'):
		queueTemp.put(request.args.get("temp"))
		return request.args.get("temp")
	return "test"

@app.route('/test_print', methods=['GET'])
def test_print():
	print "test_print"
	return "App test print"

@app.route('/mcu_temp/get_temp', methods=['GET'])
def get_temp_():
	pointid = "67e70b71-9460-4d1b-9035-c5eee0256f86"
	patternid = "/3205/0/3206"
	tempResource = connector.postResource(pointid,patternid)
	# while not tempResource.isDone():
	# 	None
	data = json.loads(tempResource.raw_data)	
	res_id = data['async-response-id']
	while res_id not in tempDisc.keys():
		None
	tempvalue = tempDisc[res_id]
	del tempDisc[res_id]
	cur.execute("use temperature")
	sql = "insert into temp values(%s, %s, %s)"
	param = (time.strftime('%H:%M:%S'), tempvalue, time.strftime('%y:%m:%d'))
	cur.execute(sql, param)
	con.commit()
	return tempvalue
# notifications channel
@app.route('/data', methods=['PUT'])
def data_received():
	print(request.data)
	data = json.loads(request.data)
	if 'async-responses' in data.keys():
		paylaod = data['async-responses'][0]['payload']
		dePayload = base64.decodestring(paylaod)
		print dePayload
		# queueTemp.put(dePayload)
		tempDisc[data['async-responses'][0]['id']] = dePayload
	return Response(status=204)

if __name__ == "__main__":

	cur.execute("create database if not exists temperature")
	# select the database TempHumTable
	cur.execute("use temperature")
	# create table temp for storing the temparature data if it not exists
	cur.execute("create table if not exists temp(time TIME, temperature FLOAT(4,2), date DATE)")
	# # clean the temp & hum table everyday
	# curdate = time.strftime('%y:%m:%d')
	# cur.execute("delete from temp where date < %s", [curdate])
	# commit update to the database
	con.commit()
	print 'init database successfully!'
	socketio.run(app,host='0.0.0.0', port=81,debug=False, use_reloader=False)
	print 'All services started --'


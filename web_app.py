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

app = Flask(__name__)
socketio = SocketIO(app,async_mode='threading')
queueTemp = Queue.Queue(maxsize = 30)
tempDisc={}

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

@app.route('/get_pattern_resource',methods=['GET'])
def get_pattern_resource():
	if(request.args.get("value")!='1'):
		epPatternResource = connector.postResource(request.args.get("pointid"),request.args.get("patternid"),request.args.get("value"))
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
	return render_template("tpl_temp_resources.html",pointid=request.args.get("pointid"),tempid=request.args.get("patternid"));

@app.route('/mcu_temp', methods=['GET'])
def get_mcu_temp():
	pointid = "67e70b71-9460-4d1b-9035-c5eee0256f86"
	patternid = "/3205/0/3206"
	return render_template("mcu_temp.html")

@app.route('mcu_temp_weekly', methods=['GET'])
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
	socketio.run(app,host='0.0.0.0', port=81,debug=True)


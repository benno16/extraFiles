import subprocess
import flask
#import json
from flask import Flask, render_template, url_for, request, json, Response, jsonify
from flask_jsonrpc import JSONRPC
from ui import ui_api

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)
app.register_blueprint(ui_api)

# JSON RPC

# Variables 
devices = []
response = []
exportActive = False
storageDeviceList = []

# Classes
class StorageDevice: 
	sdCount = 0
	'common base class for all storage devices'
	def __init__ (self, id, mountpoint, info, source):
		self.id = id
		self.mountpoint = mountpoint
		self.info = info
		self.source = source
		self.exported = False
		self.target = ""
		StorageDevice.sdCount += 1
		
	def displayStorageDevice(self):
		print "Storage Device ID %d" % StorageDevice.id

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# Helper Functions

def execute_command(exe_cmd):
    proc = subprocess.Popen(exe_cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
    out = proc.stdout.read()
    err = proc.communicate()
    #print "Exe Output: " + out
    return out

def read_data(proc_output):
	# if done already previously, clear the array
	global exportActive
	if exportActive == True: 
		return
	else:
		del storageDeviceList[:]
	i = -1
	# lets get our individual lines
	for entry in proc_output.split('\n'):
		# lets see if its actually worth working with: 
		if len ( entry ) > 1:
			i = i + 1
			#print "ID: ", i, " Value: ", entry
			ld = entry.split()
			#print "ID: ", ld[0], " Value: ", ld[1], " other: ", ld[2]
			storageDeviceList.append( StorageDevice(i, ld[0][:-1], ld[1], ld[2][1:-1]) )
			devices.append( { 	"id" : i, 
								"moutpoint" : ld[0][:-1], 
								"info" : ld[1], 
								"source" : ld[2][1:-1] } )
								
def get_exe_output(proc_output):
	resultString = ""
	for entry in proc_output.split('\n'):
		resultString = resultString + entry
	return resultString

#	Three commands are to be executed:
#	1: tgtadm --lld iscsi --op new --mode target --tid=1 --targetname iqn.1997-04.ie.ucd:firebrick-target-loop0
#	2: tgtadm --lld iscsi --op new --mode logicalunit --tid 1 --lun 1 -b /dev/loop0
#	3: tgtadm --lld iscsi --op bind --mode target --tid 1 -I ALL
def tgtadmAdd(sd):
	mp = getattr(sd, 'mountpoint')
	target = "iqn.1997-04.ie.ucd:firebrick-target-" + getattr(sd, 'mountpoint')[5:]
	tid = getattr(sd, 'id') + 1
	
	tgtatm_cmd = ['sudo', 'tgtadm', '--lld', 'iscsi', '--op', 'new', '--mode', 'target', '--tid', str(tid), '--targetname', target]
	get_exe_output(execute_command(tgtatm_cmd))

	tgtatm_cmd = ['sudo', 'tgtadm', '--lld', 'iscsi', '--op', 'new', '--mode', 'logicalunit', '--tid', str(tid) , '--lun', '1', '-b', mp]
	get_exe_output(execute_command(tgtatm_cmd))

	tgtatm_cmd = ['sudo', 'tgtadm', '--lld', 'iscsi', '--op', 'bind', '--mode', 'target', '--tid', str(tid), '-I', 'ALL']
	get_exe_output(execute_command(tgtatm_cmd))
	
	setattr(sd, 'exported', True)
	setattr(sd, 'target', target)
	
	global exportActive
	exportActive = True
	
	response.append ({ "id" : getattr(sd, 'id')})
	response.append ({ "exported" : getattr(sd, 'exported')})
	response.append ({ "target" : getattr(sd, 'target')})
	
# 	One command is to be executed:
#	tgtadm --lld iscsi --op delete --mode target --tid 1
#	Possible Error: tgtadm: this target is still active
def tgtadmDel(sd):
	tid = getattr(sd, 'id') + 1
	tgtatm_cmd = ['sudo', 'tgtadm', '--lld', 'iscsi', '--op', 'delete', '--force', '--mode', 'target', '--tid', str(tid)]
	
	global exportActive
	if len (get_exe_output(execute_command(tgtatm_cmd))) > 5:
		response.append ({ "error" : "Target probably still in use"})
	else: 
		setattr(sd, 'exported', False)
		setattr(sd, 'target', "")
		exportActive = False
		response.append ({ "success" : "Target successfully removed"})
	
# 	One command is to be executed:
#	tgtadm --lld iscsi --op show --mode target
#	tgtadm --lld iscsi --op show --mode conn --tid 1
# 	not pretty yet ;) 
def tgtadmShow():
	returnS = ""
	for sd in storageDeviceList:
		if getattr(sd, 'exported') == True:
			tgtatm_cmd = ['sudo', 'tgtadm', '--lld', 'iscsi', '--op', 'show', '--mode', 'con', '--tid', str(getattr(sd, 'id')+ 1)]
			returnS = returnS + get_exe_output(execute_command(tgtatm_cmd))
			print returnS
	
	return returnS

# Start Get Devices Function
def getDevicesImp():
	response = []

	read_data(execute_command(['sudo', 'losetup', '-a']))
	
	#return devices			#default good output
	
	# make even better output by appending to response list. 
	if len(storageDeviceList) <= 0:
		response.append({"error" : "no devices found"})
	else: 
		for sd in storageDeviceList:
			#response.append(sd.to_JSON())
			response.append( { 	"id" : getattr(sd,'id'), 
								"mountpoint" : getattr(sd,'mountpoint'), 
								"exported" : getattr(sd,'exported'), 
								"info" : getattr(sd,'info'), 
								"target" : getattr(sd,'target'), 
								"source" : getattr(sd,'source') } )
		
	return response 
	
# Start Export Function
def exportOverIscsiJSONImp(device):
	response[:] = []
	foundsd = False
	for sd in storageDeviceList:
		if getattr(sd, 'id') == device: 
			foundsd = True
			if getattr(sd, 'exported') == True:
				response[:] = []
				response.append ({"success" : "Device already exported"})
			else:	#export the device
				tgtadmAdd(sd)
	
	if foundsd == False:
		return [{"error" : "The provided device ID is invalid"}]
	
	return response
	
# Start Hide Function
def hideDevJSONImp(device):
	response[:] = []
	foundsd = False
	for sd in storageDeviceList:
		if getattr(sd, 'id') == device: 
			foundsd = True
			if getattr(sd, 'exported') == True:
				tgtadmDel(sd)
				
			else:	#export the device
				return [{"error" : "Device not exported"}]
	
	if foundsd == False:
		return [{"error" : "The provided device ID is invalid"}]
	
	return response
	
	

# End Get Devices Function. 

@jsonrpc.method('preview.getDevices', doIt=getDevicesImp)
def getDevicesJSON():
    return getDevicesImp()
	
	
@jsonrpc.method('preview.exportOverIscsi(device = int) -> Object', validate = True)
def exportOverIscsiJSON(device):
    return exportOverIscsiJSONImp(device)
	
	
@jsonrpc.method('preview.hideDev(device = int) -> Object', validate = True)
def hideDevJSON(device):
    return hideDevJSONImp(device)

	
#@jsonrpc.method('preview.showStatus')
#def showStatusJSON():
#    return tgtadmShow()

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	


# WEB Application
@app.route("/")
def homepage():

	title = "Preview Module"
	paragraph = ["Paragraph Content That Rocks","Paragraph Content That Rocks","Paragraph Content That Rocks","Paragraph Content That Rocks","Paragraph Content That Rocks","Paragraph Content That Rocks","Paragraph Content That Rocks"]
	pageType = "index"
	#read_data(get_disk_data())
	#return Response(json.dumps(devices),  mimetype='application/json')
	return render_template("index.html", title = title, paragraph = paragraph, pageType = pageType)
	
@app.route("/about")
def aboutPage():

	title = "About this module"
	paragraph = ["This is the about page"]
	version = "Version: 1.2.3" 
	pageType = "about"

	return render_template("index.html", title = title, paragraph = paragraph, version = version, pageType = pageType)
	
@app.route("/about/contact")
def contactPage():

	title = "About this module"
	paragraph = ["This is the about page"]
	version = "Version: 1.2.3" 
	pageType = "contact"

	return render_template("index.html", title = title, paragraph = paragraph, version = version, pageType = pageType)
	
	
	

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5004)

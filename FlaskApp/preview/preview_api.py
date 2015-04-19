import subprocess
import flask
import os
import socket
from flask import Flask, render_template, url_for, request, json, Response, jsonify
from rtslib import *

from preview import jsonrpc

# JSON RPC

# Variables 
devices = []
response = []
exportActive = False
storageDeviceList = []
iscsi = FabricModule("iscsi")

# Classes
class StorageDevice: 
	sdCount = 0
	global iscsi
	'common base class for all storage devices'
	def __init__ (self, id, mountpoint, info, source):
		self.id = id
		self.mountpoint = mountpoint
		self.info = info
		self.source = source
		self.exported = False
		self.target = ""
		self.blk = ""
		self.itarget =  ""
		self.tpg = ""
		self.lun = ""
		StorageDevice.sdCount += 1
		
	def displayStorageDevice(self):
		print "Storage Device ID %d" % StorageDevice.id

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# Helper Functions
if os.name != "nt":
	import fcntl
	import struct

	def get_interface_ip(ifname):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
								ifname[:15]))[20:24])

def get_lan_ip():
	ip = socket.gethostbyname(socket.gethostname())
	if ip.startswith("127.") and os.name != "nt":
		interfaces = [
			"eth0",
			"eth1",
			"eth2",
			"wlan0",
			"wlan1",
			"wifi0",
			"ath0",
			"ath1",
			"ppp0",
			]
		for ifname in interfaces:
			try:
				ip = get_interface_ip(ifname)
				break
			except IOError:
				pass
	return ip

# check if TGT service running!
# for demo deactivated! 
def checkTGT():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect(('127.0.0.1', 3260))
		s.shutdown(2)
		return True
	except:
		return True
# this should say False!

def execute_command(exe_cmd):
	proc = subprocess.Popen(exe_cmd, stdout=subprocess.PIPE,
									 stderr=subprocess.PIPE)
	out = proc.stdout.read()
	err = proc.communicate()
	#print "Exe Output: " + out
	return out

def read_data(proc_output):
	newstorageDeviceList = []
	for sd in storageDeviceList:
		newstorageDeviceList.append(sd)
	del storageDeviceList[:]
	i = -1
	# lets get our individual lines
	for entry in proc_output.split('\n'):
		# lets see if its actually worth working with: 
		if len ( entry ) > 1:
			i = i + 1
			#print "ID: ", i, " Value: ", entry
			ld = entry.split()
			
			doesExist = False
			
			for sd in newstorageDeviceList:
				if getattr(sd, 'mountpoint') == ld[0][:-1]:
					doesExist = True
					storageDeviceList.append(sd)

			if (doesExist == False):
				#print "ID: ", ld[0], " Value: ", ld[1], " other: ", ld[2]
				storageDeviceList.append( StorageDevice(i, ld[0][:-1], ld[1], ld[2]) )
								
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
	target = "iqn.1997-04.ie.ucd:firebrick-target-" + mp[5:]
	tid = getattr(sd, 'id') + 1

	blk = BlockStorageObject(mp[5:],mp,"",True)

	global iscsi
	
	itarget = Target(iscsi, target)
	tpg = TPG(itarget, tid)

	portal = NetworkPortal(tpg, "0.0.0.0", 3260)

	lun = LUN(tpg, getattr(sd, 'id'), blk)

	tpg.set_attribute("authentication", "0")
	tpg.set_attribute("demo_mode_write_protect", "0")
	tpg.set_attribute("generate_node_acls", "1")
	tpg.set_attribute("cache_dynamic_acls", "1")
	tpg.set_attribute("demo_mode_discovery", "1")
	tpg.set_parameter("AuthMethod", "None")

	tpg._set_enable(True)

	setattr(sd, 'exported', True)
	setattr(sd, 'target', target)
	setattr(sd, 'itarget', itarget)
	setattr(sd, 'blk', blk)
	setattr(sd, 'tpg', tpg)
	setattr(sd, 'lun', lun)
	
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
	
	global exportActive
	blk = getattr(sd, 'blk')
	itarget = getattr(sd, 'itarget')
	lun = getattr(sd, 'lun')
	tpg = getattr(sd, 'tpg')

	lun.delete()
	tpg.delete()
	itarget.delete()
	blk.delete()
	
#	clear_cmd = ['targetctl', 'clear']
#	execute_command(clear_cmd)

#	restart_cmd = ['/etc/init.d/S50target', 'restart']
#	execute_command(restart_cmd)

	if 1 > 5:
		response.append ({ "error" : "Target probably still in use"})
	else: 
		setattr(sd, 'exported', False)
		setattr(sd, 'target', "")		
		setattr(sd, 'itarget', "")
		setattr(sd, 'blk', "")
		setattr(sd, 'tpg', "")
		setattr(sd, 'lun', "")
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
			tgtatm_cmd = ['tgtadm', '--lld', 'iscsi', '--op', 'show', '--mode', 'con', '--tid', str(getattr(sd, 'id')+ 1)]
			returnS = returnS + get_exe_output(execute_command(tgtatm_cmd))
			print returnS
	
	return returnS

# Start Get Devices Function
def getDevicesImp():
	response = []

	read_data(execute_command(['losetup', '-a']))
	
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
	print "hideDevJSONImp initiated: " + str(device)
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
	
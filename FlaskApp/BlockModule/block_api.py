# FIREBRICK BLOCK DEVICE MODULE
# Author: Julie O'Dea
# Import libraries
from flask import Flask, render_template, request, jsonify, url_for, Response  
from flask_jsonrpc import JSONRPC
import os,sys
import subprocess as sub 

from BlockModule import jsonrpc


#Global variables
LoopDeviceList = []
BlockDeviceList = []
response = []
#refreshURL = "127.0.0.1"
refreshURL = "178.62.22.54"

# Classes
class LoopDevice: 
    ldCount = 0
    'common base class for all loop devices'
    def __init__ (self, id, mountpoint, info, source):
        self.id = id
        self.mountpoint = mountpoint
        self.info = info
        self.source = source
        LoopDevice.ldCount += 1
   
class BlockDevice: 
    bdCount = 0
    'common base class for all block devices'
    def __init__ (self, id, type, name, serial, size):
        self.id = id
        self.type = type
        self.name = name
        self.serial = serial 
        self.size = size 
        BlockDevice.bdCount += 1   
    def __contains__(self, key):
        return key.name == self.name	

def execute_command(exe_cmd):
       proc = sub.Popen(exe_cmd, stdout=sub.PIPE, 
                                        stderr=sub.PIPE)
       out = proc.stdout.read()
       err = proc.communicate()
       return(out)
   
def read_data(proc_output):
    del LoopDeviceList[:]
    i = -1
    for entry in proc_output.split('\n'):
        if len ( entry ) > 1:
            i = i + 1
            ld = entry.split()
            LoopDeviceList.append( LoopDevice(i, ld[0][:-1], ld[1], ld[2]) )


def interpret_lshw(proc_output):
    i = 0
    for entry in proc_output.split('*'):
            if len ( entry ) > 1: 
                hwline = entry.split('\n')
                if (hwline[0] == "-disk"):
                    j = 0
                    dserial = "not available"
                    dsize = ""
                    dname = ""
                    while (j < 12) :
                        temp = hwline[j] 
                        if (temp[7:18] == "description"):
                            dtype = temp[20:35]
                        elif (temp[7:14] == "logical"):
                            dname = temp[21:36]                     
                        elif ( temp[7:13] == "serial"):
                            dserial = temp[15:35]
                        elif ( temp[7:11] == "size"):
                            dsize = temp[12:30]
                            break
                        j = j + 1
                    block = BlockDevice(i,dtype, dname, dserial, dsize)
                    if block not in BlockDeviceList:
                        BlockDeviceList.append(block) 
                        i = i + 1
    return  
	
def interpret_lsblk(proc_output):
	dserial = "not available"
	i = 0
	for entry in proc_output.split('\n'):
		if len ( entry ) > 1:
			ld = entry.split()
			if (ld[5] != "loop") and (ld[5] != "part") and (ld[5] != "rom"):
				block = BlockDevice(i, ld[5], "/dev/" + ld[0], dserial, ld[3])
				if block not in BlockDeviceList:
					BlockDeviceList.append(block)          
					i = i + 1 
            
def getDevicesIn():
    response = []
    read_data(execute_command(['losetup', '-a']))
    if len(LoopDeviceList) <= 0:
        response.append({"Message" : "no devices found"})
    else: 
        for sd in LoopDeviceList:
            response.append( {     "id" : getattr(sd,'id'), 
                                "mountpoint" : getattr(sd,'mountpoint'), 
                                "info" : getattr(sd,'info'), 
                                "source" : getattr(sd,'source') } )        
    return(response) 
 

def getBlocksIn():
    del BlockDeviceList[:] 
    response = []
    interpret_lshw(execute_command(['lshw', '-class', 'disk']))
#    interpret_lsblk(execute_command(['lsblk', '-ln']))
    if len(BlockDeviceList) <= 0:
        response.append({"Message" : "no devices found"})
    else: 
        for sd in BlockDeviceList:
            response.append( {     "id" : getattr(sd,'id'), 
                                "type" : getattr(sd,'type'),
                                "name" : getattr(sd,'name'),
                            "serial" : getattr(sd,'serial'), 
                                "size" : getattr(sd,'size') } )           
    return(response) 

def MountDevice(devname): 
    response = []
    mountstring = "losetup -r -f %s" % devname 
    result=os.system(mountstring)
    if result != 0:
        message = "An error occurred with mount of %s, please check your input. The device name must be specified in full (e.g. /dev/sda)" % devname
    else:
        message = "%s successfully mounted" % devname
    response.append({"Message" : message })
    return(response)  

def RemoveLoop(devname):
    response = []
# detach the specified loopback device     
    umountstring = "losetup -d %s" % devname   
    result = os.system(umountstring)
           
    if result != 0:
            message = "An error occurred with detach of %s, please check your input. The mountpoint must be specified in full (e.g. /dev/loop0)" % devname
    else: 
            message = "%s successfully detached" % devname
    response.append({"Message" : message })
    return(response)

    
#  METHOD FOR JSON-RPC
@jsonrpc.method('BlockModule.List_Blocks')

def Available_dev_json():
    return getBlocksIn()

@jsonrpc.method('BlockModule.List_Loops')

def mounted_dev_json():
    return getDevicesIn()

@jsonrpc.method('BlockModule.Mount_as_Loop')

def mount_device_json(device): 
    return MountDevice(device)

@jsonrpc.method('BlockModule.Remove_Loop')

def unmount_device_json(device):
    return RemoveLoop(device)

    



# FIREBRICK BLOCK DEVICE MODULE
# Author: Julie O'Dea
# Import libraries
from flask import Flask, render_template, request, jsonify, url_for, Response  
from flask_jsonrpc import JSONRPC
import os,sys
import subprocess as sub 
#from ui import ui_api


app = Flask(__name__)
jsonrpc=JSONRPC(app,'/api',enable_web_browsable_api=True)
#app.register_blueprint(ui_api)

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
            LoopDeviceList.append( LoopDevice(i, ld[0][:-1], ld[1], ld[2][1:-1]) )


def read_data2(proc_output):
    del BlockDeviceList[:]  
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
                    BlockDeviceList.append(BlockDevice(i,dtype, dname, dserial, dsize))         
                    i = i + 1   

    return  
            
def getDevicesIn():
    response = []
    read_data(execute_command(['losetup', '--all']))
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
    response = []
    read_data2(execute_command(['lshw', '-class', 'disk']))
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

# web application
@app.route('/')
def Homepage():
    title = "Block Module"
    paragraph = getBlocksIn()
    paragraph2 = getDevicesIn()
    pageType = "index"
    return render_template("index.html",title = title, paragraph = paragraph, paragraph2 = paragraph2, pageType = pageType)

@app.route('/Mount', methods = ['POST'])
def Mount_Device():
    devname = request.form.get('Mdevice')
    title = "Block Module"
    refresh = True
    response = MountDevice(devname)
    return render_template("index.html", title = title, refresh = refresh, refreshURL = refreshURL)

@app.route('/Unmount', methods = ['POST'])
def Unmount_device():
    devname = request.form.get('Udevice')  
    title = "Block Module"
    refresh = True 
    response = RemoveLoop(devname) 
    return render_template("index.html", title = title, refresh = refresh, refreshURL = refreshURL)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002)
    



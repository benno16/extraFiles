# Author: Paul Martin
# Firebrick Imager Module

#!/usr/bin/python
import flask
import time
import subprocess as sub
import subprocess
import re
import fcntl
import sys
import os
import filecmp
from flask import Flask, render_template, request, jsonify, url_for, Response  
from flask_jsonrpc import JSONRPC

app = Flask(__name__)
jsonrpc=JSONRPC(app,'/api',enable_web_browsable_api=True)


#Global variables
LoopDeviceList = []
devices = []
response = []
sub1 = "/dev/"
refreshURL = "178.62.22.54"

class BlockDevice: 
    bdCount = 0
    'common base class for all block devices'
    def __init__ (self, id, type, name, size):
        self.id = id
        self.type = type
        self.name = name
        self.size = size 
        BlockDevice.bdCount += 1
        
class LoopDevice:
    ldCount = 0
    'common base class for all loop devices'
    def __init__ (self, id, mountpoint, info, source):
        self.id = id
        self.mountpoint = mountpoint
        self.info = info
        self.source = source
        LoopDevice.ldCount += 1



p1 = None
last_progr = "0"
prog_re = re.compile(r".*\[([0-9]+)\%.*")

def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.read()
    except:
        return ""

@app.route('/')
def Homepage():
    title = "Imager"
    paragraph = getDevicesIn()
    pageType = "index"
    return render_template("index.html",title = title,paragraph = paragraph,pageType = pageType)

#Function by written by Julie O'Dea 

def execute_command(exe_cmd):
    proc = sub.Popen(exe_cmd, stdout=sub.PIPE, 
        stderr=sub.PIPE)
    out=proc.stdout.read()
    err = proc.communicate()
    return out 

#Function by written by Julie O'Dea    

def read_data(proc_output):
    del LoopDeviceList[:]
    i = -1
    for entry in proc_output.split('\n'):
        if len ( entry ) > 1:
            i = i + 1
            ld = entry.split()
            LoopDeviceList.append( LoopDevice(i, ld[0][:-1], ld[1], ld[2][1:-1]) )
            devices.append( {     "id" : i,
                                "mountpoint" : ld[0][:-1],
                                "info" : ld[1],
                                "source" : ld[2][1:-1] } )
#Function by written by Julie O'Dea 
  
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


@app.route('/done',  methods = ['GET','POST'])
def done():
    return flask.send_file('templates/done.html')

@app.route('/fail',  methods = ['GET','POST'])
def fail():
    return flask.send_file('templates/fail.html')

@app.route('/mount',  methods = ['GET','POST'])
def mount():
    return flask.send_file('templates/mount.html')

@app.route('/image',  methods = ['GET','POST'])
def image():
    return flask.send_file('templates/image.html')


@app.route('/mountusb', methods = ['POST','GET'])
def mountusb():
    os.system('mkdir /media/images')
    partitionsFile = open("/proc/partitions")
    lines = partitionsFile.readlines()[2:]#Skips the header lines
    for line in lines:
        words = [x.strip() for x in line.split()]
        minorNumber = int(words[1])
        deviceName = words[3]
        if minorNumber % 16 == 0:
            path = "/sys/class/block/" + deviceName
            if os.path.islink(path):
                if os.path.realpath(path).find("/usb") > 0:
                    a = "/dev/%s" % deviceName +"1"
                    cmd = 'mount %s /media/images' % a
                    os.system(cmd)
    return flask.send_file('templates/image.html')

@app.route('/copy', methods = ['POST','GET'])
def get_page():
    global p1
    p1 = subprocess.Popen(['dcfldd if=/dev/loop0 hash=md5,sha256 hashconv=after bs=512 conv=noerror of=/media/images/image.dd sizeprobe=if 2>&1'],shell=True,
            stdout=subprocess.PIPE)
    return flask.send_file('templates/progress.html')

@app.route('/progress', methods = ['GET','POST'])
def progress():
    def generate():
        global p1
        global last_progr         
        global prog_re
        global finish_re
        line = non_block_read(p1.stdout)
        print line
        x=prog_re.match(line)
        if x != None :
            last_progr = x.group(1)
        if "records" in line:
            last_progr = "100"
        return "data:" + last_progr +"\n\n"
    return flask.Response(generate(), mimetype= 'text/event-stream')

@app.route('/hashcheck', methods = ['GET','POST'])

def hashcheck():
    os.system ('sha1sum /dev/loop0 > /root/FlaskApp/ImagerModule/Devhash.txt')
    os.system ('md5sum /dev/loop0 >> /root/FlaskApp/ImagerModule/Devhash.txt')
    os.system ('cut -c 1-32 /root/FlaskApp/ImagerModule/Devhash.txt > /root/FlaskApp/ImagerModule/devcomp.txt')
    os.system ('sha1sum /media/images/image.dd > /root/FlaskApp/ImagerModule/ddhash.txt')
    os.system ('md5sum /media/images/image.dd   >> /root/FlaskApp/ImagerModule/ddhash.txt')
    os.system ('cut -c 1-32 /root/FlaskApp/ImagerModule/ddhash.txt > /root/FlaskApp/ImagerModule/ddcomp.txt')
    if filecmp.cmp('/root/FlaskApp/ImagerModule/devcomp.txt','/root/FlaskApp/ImagerModule/ddcomp.txt'):
        return flask.send_file('templates/hash.html')
    else:
        return flask.send_file('templates/fail.html')
    

#  METHOD FOR JSON-RPC


@jsonrpc.method('imager.mount_usb_drive')
def Mount_usb_drivb():
   return("Mounted")

@jsonrpc.method('imager.copydisk')
def dd_copy_device():
    return ("copied")

@jsonrpc.method('imager.haskcheck')
def verify_Image_hash():
    return ("Verified")

if __name__ == '__main__':
	app.run(debug=True, port=5005, host='0.0.0.0')


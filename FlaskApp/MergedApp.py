from flask import Flask,request,render_template
from flask_jsonrpc import JSONRPC
from datetime import datetime

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api',enable_web_browsable_api=True)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response
	
	
@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )	
	
""" ModStorage 
"""

#import ModStorage.api

@app.route('/modstorage')
def modstorage():
    return render_template(
        'storage.html',
        title='modstorage',
        year=datetime.now().year,
    )
	
""" ModVizX2 
"""	

#import ModStorage.api

@app.route('/modVizX2')
def modvizx2():
    return render_template(
        'ModVizX2.html',
        title='modVizX2',
        year=datetime.now().year,
    )

""" Mod preview  
"""
import preview.preview_api	

from preview.preview_api import getDevicesImp
from preview.preview_api import checkTGT
from preview.preview_api import exportOverIscsiJSONImp
from preview.preview_api import hideDevJSONImp

@app.route('/modPreview')
def modpreview():	
	title = "Preview Module"
	paragraph = getDevicesImp()
	pageType = "index"
	tgtUp = checkTGT()
	return render_template("preview.html", title = title, paragraph = paragraph, pageType = pageType, tgtUp = tgtUp)  

@app.route('/modPreview/about')
def modpreviewAbout():	
	title = "About this module"
	paragraph = ["Benedikt Riedel"]
	version = "Version: 1.2.3" 
	pageType = "about"
	return render_template("preview.html", title = title, paragraph = paragraph, version = version, pageType = pageType)  	

@app.route("/modPreview/exportOverIscsi", methods = ['POST'])
def exportOverIscsiHTTP():
	deviceId = int(request.form['deviceId'])
	exportOverIscsiJSONImp(deviceId)
	return modpreview()

	
@app.route("/modPreview/hideDev", methods = ['POST'])
def hideDevHTTP():
	deviceId = int(request.form['deviceId'])	
	hideDevJSONImp(deviceId)
	return modpreview()
	
"""Block module
""" 
import BlockModule.block_api

from BlockModule.block_api import getBlocksIn
from BlockModule.block_api import getDevicesIn
from BlockModule.block_api import RemoveLoop
from BlockModule.block_api import MountDevice

# web application
@app.route('/modBlock')
def BlockHomepage():
	title = "Block Module"
	paragraph = getBlocksIn()
	paragraph2 = getDevicesIn()
	pageType = "index"
	return render_template("block.html",title = title, paragraph = paragraph, paragraph2 = paragraph2, pageType = pageType)

@app.route('/modBlock/Mount', methods = ['POST'])
def Mount_Device():
	devname = request.form.get('Mdevice')
	response = MountDevice(devname)
    
	title = "Block Module"
	paragraph = getBlocksIn()
	paragraph2 = getDevicesIn()
	pageType = "index"
	
	return render_template("block.html",title = title, paragraph = paragraph, paragraph2 = paragraph2, pageType = pageType)

@app.route('/modBlock/Unmount', methods = ['POST'])
def Unmount_device():
	devname = request.form.get('Udevice') 
	response = RemoveLoop(devname) 	
	
	title = "Block Module"
	paragraph = getBlocksIn()
	paragraph2 = getDevicesIn()
	pageType = "index"
	
	return render_template("block.html",title = title, paragraph = paragraph, paragraph2 = paragraph2, pageType = pageType)

#imaging module
@app.route('/modImage')
def modimagepage():
    return render_template(
        'modImage.html',
        title='modImage',
        year=datetime.now().year,
    )
	
	
if __name__ == '__main__':
	app.run("0.0.0.0", 5050)
	
from flask import Flask
from flask import render_template, request, jsonify, url_for, Response  
from flask_jsonrpc import JSONRPC
#import os, sys 

#base_dir = os.path.dirname(__file__)
#print "base dir:", base_dir
#package_dir_a = os.path.join(base_dir, 'FlaskApp')
#sys.pathinsert(0, package_dir_a)
import block


app = Flask(__name__)
jsonrpc=JSONRPC(app,'/api',enable_web_browsable_api=True)


#def import_(filename):
#    path, name = os.path.split(filename)
#    name, ext = os.path.splitext(name)
#    print "before: %s in sys.modules ==" % name, name in sys.modules 
#    file, filename, data = imp.find_module(name, [path])
#    mod = imp.load_module(name, file, filename, data)
#    print "after: %s in sys.modules ==" % name, name in sys.modules
#    return mod 

@app.route('/')
def Homepage():
    title = "Block Module"
    paragraph = block.getBlocksIn()
    paragraph2 = block.getDevicesIn()
    pageType = "index"
    return render_template("index.html",title = title, paragraph = paragraph, paragraph2 = paragraph2, pageType = pageType)

@app.route('/Mount', methods = ['POST'])
def Mount_Device():
    devname = request.form.get('Mdevice') 
    title = "Block Module"
    refresh = True
    response = block.MountDevice(devname) 
    return render_template("index.html", title = title, refresh = refresh, refreshURL = block.refreshURL)

@app.route('/Unmount', methods = ['POST'])
def Unmount_device():
    devname = request.form.get('Udevice')  
    title = "Block Module"
    refresh = True 
    response = block.RemoveLoop(devname) 
    return render_template("index.html", title = title, refresh = refresh, refreshURL = block.refreshURL) 

if __name__ == '__main__':
    app.run(debug=False,port=5002)
    

    
    
    
             




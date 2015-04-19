from flask import Flask, render_template, request, jsonify, url_for, Response  
from flask_jsonrpc import JSONRPC
import os.path, sys
import md5 
import imp 
import traceback


def load_module(code_path):
    try:
        try:
            code_dir = os.path.dirname(code_path)
            code_file = os.path.basename(code_path)
            fin = open(code_path, 'rb')
            return imp.load_source(md5.new(code_path).hexdigest(), code_path, fin)
        finally:
            try: fin.close()
            except: pass
    except ImportError, x:
        traceback.print_exc(file=sys.stderr)
        raise 
    except:
        traceback.print_exc(file=sys.stderr)
        raise   
    
app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)

load_module('/root/FlaskApp/BlockModule/__init__.py')
#load_module('/root/FlaskApp/preview/__init__.py')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
    
             




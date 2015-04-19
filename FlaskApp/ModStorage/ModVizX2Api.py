import os.path
from ModStorage import jsonrpc
from flask import jsonify

configFileName = 'modVizX2.data'

@jsonrpc.method('ModVizX2.loadConfiguration')
def loadConfiguration():
    global configFileName
    if os.path.exists(configFileName):
        f = open(configFileName)
        result = f.read()
        f.close()
        return result
    return ''

@jsonrpc.method('ModVizX2.saveConfiguration')
def saveConfiguration(config):
    global configFileName
    f = open(configFileName,'w')
    f.writelines(config)
    f.close()
    return True
    
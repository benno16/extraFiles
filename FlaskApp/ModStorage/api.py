import json
import jsonpickle
import uuid
import os.path
from ModStorage import jsonrpc
from flask import jsonify
from ModStorage.mountHelper import mountShare
from ModStorage.mountHelper import unmountShare

storageDbFileName = 'storages.json'
storages = []

if os.path.exists(storageDbFileName):
    f = open(storageDbFileName)
    storages = jsonpickle.decode(f.read())
    f.close()
    for s in storages: 
        print('Start mount:' + s['Name'] + '\n' )
        s['IsActive'] = mountShare(s)


@jsonrpc.method('App.index')
def index():
    return u'Welcome to Flask JSON-RPC'

@jsonrpc.method('Storage.getStorages')
def getStorages():
    global storages  
    return json.loads(jsonpickle.encode(storages))

@jsonrpc.method('Storage.getActiveStorages')
def getActiveStorages():
    return ""

@jsonrpc.method('Storage.createStorage')
def createStorage(storageModel):
    global storages
    m= jsonpickle.decode(storageModel)
    m['ID'] = uuid.uuid4().hex
    storages.append(m)
    saveStoragesToDisk()
    mountShare(m)
    return m['ID'];

@jsonrpc.method('Storage.updateStorage')
def updateStorage(storageModel):
    global storages
    m= jsonpickle.decode(storageModel)
    index = 0
    for s in storages:       
        if s['ID'] == m['ID']:
            storages[index] = m
            saveStoragesToDisk()
            return True
        index+=1
    return False;

@jsonrpc.method('Storage.deleteStorage')
def deleteStorage(itemId):
    global storages
    for s in storages:       
        if s['ID'] == itemId:
            storages.remove(s)
            saveStoragesToDisk()
            return True        
    return False;

@jsonrpc.method('Storage.testConnection')
def testConnection(storageModel):
    m= jsonpickle.decode(storageModel)
    if not m['ID']:
        m['ID'] = uuid.uuid4().hex
    if mountShare(m):
        unmountShare(m)
        return True
    return False;

def saveStoragesToDisk():
    global storageDbFileName
    global storages
    f = open(storageDbFileName,'w')
    f.writelines(jsonpickle.encode(storages))
    f.close()

class StorageItem:
    def __init__(self):
        self.ID = uuid.uuid4().hex
        self.Name = ""
        self.Type = ""
        self.UserName = ""
        self.Password = ""
        self.Path = ""
        self.IsActive = True
        self.LastError = ""
        self.MountedTo = ""


    
# Author: Julie O'Dea
# function which takes a provided path (mypath) and identifies all of folders in that path
# for example: if folder foo contained 2 directories (dira & dirb), if path of /foo was provided
# this function would return a JSON structure as follows:
#  [{ 'Name': 'dira', 'path' : '/foo/dira' }
#   { 'Name': 'dirb', 'path' : '/foo/dirb' }]
#

import os.path, sys
dirinfo = [] 

def find_folders(mypath):
    for root, dirs, f in os.walk(mypath):
        break 
    i = 0
    if len(dirs) <= 0:
        message = "no folders were found in the path provided"
    else:
        for sd in dirs:
            temp = os.path.join(root,dirs[i]) 
            dirinfo.append( {"Name" : dirs[i],
                            "path" : temp }) 
            i = i + 1 
        message = "success"    
    return(dirinfo,message)       
    
             




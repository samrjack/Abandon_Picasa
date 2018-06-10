#!/usr/bin/python3

import fileinput
import json
import stat
import os
from jaraco.windows import filesystem

'''
def has_hidden_attribute(filepath):
    try:
        print(os.stat(filepath))
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    except PermissionError:
        return True
'''
def has_hidden_attribute(filepath):
    return filesystem.GetFileAttributes(filepath).hidden

picture_formats = ["jpeg","tif","tif","bmp","gif","psd","png","tga","mpg","mod","mmv","tod","wmv","asf","avi","dvx","mov","m4v","3gp","3g2","mp4","m2t","m2ts","mts","mkv","avi","asf","wmv","mpg","m2t","m2ts","mts","mkv","avi","asf","wmv","mpg","m2t","mmv","m2ts","wma","mp3"]

pictures = {}

f = open("picasa_files.txt", 'r')
path = f.readline()
while os.path.basename(os.path.dirname(path)) != "Users":
    path = os.path.dirname(path)

for root, dirs, files in os.walk(path, topdown=True):
    print(files)
    print(dirs)
    print(root)
    files[:] = [f for f in files if not has_hidden_attribute(os.path.join(root,f))]
    dirs[:]  = [d for d in dirs  if not has_hidden_attribute(os.path.join(root,d))]
    
    for fil in files:
        if fil.split('.')[-1] in picture_formats:
            pictures[os.path.join(root, fil)] = {}
            print(os.path.join(root, fil))

for fileName in fileinput.input():
    fileName = fileName.replace("\n","")
    directory = os.path.dirname(fileName)
    f = open(fileName, "r")
    line = f.readline()
    while True:
        if not line: 
            break
        if "[" not in line or "]" not in line or "[.album:" in line or "[Picasa]" in line:
            line = f.readline()
            continue
        
        path = directory + "/" + line.replace("\n", "").replace("[","").replace("]","")
        if path not in pictures:
            if os.path.exists(path):
                pictures[path] = {}
            else:
                line = f.readline()
                continue

        key = ""
        value = ""
        line = f.readline().replace("\"", "\\\"").replace("\n", "")
        while line and "=" in line:
            if "backup" in line:
                line = f.readline().replace("\"", "\\\"").replace("\n", "")
                continue

            if "albums=" in line:
                key = 'albums'
                value = line.split("=")[1].split(",")
            else:
                [key,value] = line.split("=", 1)
            pictures[path][key] = value
            line = f.readline().replace("\"", "\\\"").replace("\n", "")
        if "hidden" in pictures[path]:
            if pictures[path]["hidden"] == "yes":
                del pictures[path]

    f.close()
        
print(json.dumps(pictures))
outFile = open("pictures.json","w")
outFile.write(json.dumps(pictures))
outFile.close()


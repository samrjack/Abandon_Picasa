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


def makePictureJSON(picasaFiles):
    picture_formats = ["jpeg","tif","tif","bmp","gif","psd","png","tga","mpg","mod","mmv","tod","wmv","asf","avi","dvx","mov","m4v","3gp","3g2","mp4","m2t","m2ts","mts","mkv","avi","asf","wmv","mpg","m2t","m2ts","mts","mkv","avi","asf","wmv","mpg","m2t","mmv","m2ts","wma","mp3"]

    pictures = {}

    for root, dirs, files in os.walk(os.path.abspath(os.sep), topdown=True):
        files[:] = [f for f in files if not has_hidden_attribute(os.path.join(root,f))]
        dirs[:]  = [d for d in dirs  if not has_hidden_attribute(os.path.join(root,d))]
        
        for fil in files:
            if fil.split('.')[-1] in picture_formats:
                pictures[os.path.join(root, fil)] = {}
                print(os.path.join(root, fil))

    for fileName in picasaFiles:
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
            
    # outFile = open("pictures.json","w")
    # outFile.write(json.dumps(pictures))
    # outFile.close()
    return pictures



def makeAlbumJSON(picasaFiles):
    albums = {}
    for fileName in picasaFiles:
        f = open(fileName.replace("\n",""), "r")
        line = f.readline()
        # Read every line in the file
        while True:
            if not line: 
                break
            if "[.album:" not in line:
                line = f.readline()
                continue
            
            # Turn album into a dictionary entry
            line = f.readline().replace("\"", "\\\"").replace("\n", "")
            thisAlbum = {}
            while line and "=" in line:
                [key,value] = line.split("=", 1)
                thisAlbum[key] = value
                line = f.readline().replace("\"", "\\\"").replace("\n", "")

            if not "token" in thisAlbum:
                continue
            
            tok = thisAlbum["token"];
            if not tok in albums:
                albums[tok] = {}

            for k,v in thisAlbum.items():
                albums[tok][k] = v
        # Finished reading metadata file
        f.close()

    # outFile = open("album.json","w")
    # outFile.write(json.dumps(albums))
    # outFile.write(json.dumps(list(albums.values())))
    # outFile.close()
    return albums

def findPicasaFiles():
    pFiles = []
    for root, dirs, files in os.walk(os.path.abspath(os.sep), topdown=True):
        if ".picasa.ini" in files:
            pFiles.append(os.path.join(root,".picasa.ini")
    return pFiles

def main():
    pFiles  = findPicasaFiles()
    albums  = findAlbums(pFiles)
    picturs = fildPictures(pFiles)
    

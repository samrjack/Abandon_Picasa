#!/usr/bin/python3

import json
import stat
import os

from pathlib import Path

def main():
    pFiles   = findPicasaFiles()
    albums   = findAlbums(pFiles)
    pictures = findPictures(pFiles)
    
    print(pictures)

def findAlbums(picasaFiles):
    if os.path.exists(os.path.join('.', '.albums.json')):
        #TODO read file
        pass
    else:
        return __findAlbumsOnDisk(picasaFiles)

def findPictures(picasaFiles):
    if os.path.exists(os.path.join('.', '.pictures.json')):
        #TODO read file
        pass
    else:
        return __findPicturesOnDisk(picasaFiles)

def findPicasaFiles():
    pFiles = []
    for root, dirs, files in os.walk(str(Path.home()), topdown=True):
        dirs[:]  = [d for d in dirs  if not has_hidden_attribute(os.path.join(root,d))]
        if ".picasa.ini" in files:
            pFiles.append(os.path.join(root,".picasa.ini"))
            
    return pFiles
    


def has_hidden_attribute(filepath):
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN) or os.path.basename(filepath)[0] == '.'

def __findPicturesOnDisk(picasaFiles):
    picture_formats = ["jpeg","tif","tif","bmp","gif","psd","png","tga","mpg","mod","mmv","tod","wmv","asf","avi","dvx","mov","m4v","3gp","3g2","mp4","m2t","m2ts","mts","mkv","avi","asf","wmv","mpg","m2t","m2ts","mts","mkv","avi","asf","wmv","mpg","m2t","mmv","m2ts","wma","mp3"]

    pictures = {}

    for root, dirs, files in os.walk(Path.home(), topdown=True):
        files[:] = [f for f in files if not has_hidden_attribute(os.path.join(root,f))]
        dirs[:]  = [d for d in dirs  if not (d[0] == '.' or has_hidden_attribute(os.path.join(root,d)))]
        
        for fil in files:
            if fil.split('.')[-1] in picture_formats:
                pictures[os.path.join(root, fil)] = {}

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

def __findAlbumsOnDisk(picasaFiles):
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
            
            tok = thisAlbum["token"]
            if not tok in albums:
                albums[tok] = {}

            for k,v in thisAlbum.items():
                albums[tok][k] = v
        # Finished reading metadata file
        f.close()

    return albums

if __name__ == "__main__":
    main()
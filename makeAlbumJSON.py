#!/usr/bin/python3

import fileinput
import json

albums = {}
for fileName in fileinput.input():
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
        
# print(json.dumps(list(albums.values())))
outFile = open("album.json","w")
outFile.write(json.dumps(albums))
#outFile.write(json.dumps(list(albums.values())))
outFile.close()

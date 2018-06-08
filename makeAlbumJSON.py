#!/usr/bin/python3

import fileinput

outString = "[\n"
for fileName in fileinput.input():
    f = open(fileName.replace("\n",""), "r")
    line = f.readline()
    while True:
        if not line: 
            break
        if "[.album:" not in line:
            line = f.readline()
            continue
        
        line = f.readline().replace("\"", "\\\"").replace("\n", "")
        jsonString = "{"
        while line and "=" in line:
            [key,value] = line.split("=", 1)
            jsonString += '"' + key + '":"' + value + '", '
            line = f.readline().replace("\"", "\\\"").replace("\n", "")
        outString += jsonString[:-2] + '},\n'
    f.close()
        
outString = outString[:-2] + '\n]\n'
outFile = open("album.json","w")
outFile.write(outString)
outFile.close()

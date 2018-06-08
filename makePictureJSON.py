#!/usr/bin/python3

import fileinput
import os

outString = "[\n"
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
        
        jsonString = "{"

        jsonString += '"path":"' + directory + "/" + line[1:-1] + '", '

        line = f.readline().replace("\"", "\\\"").replace("\n", "")
        while line and "=" in line:
#            if "backup" in line:
 #               line = f.readline().replace("\"", "\\\"").replace("\n", "")
  #              continue

            if "albums=" in line:
                key = '"albums"'
                value = line.split("=")[1].split(",")
                value = list(map(lambda x: '"' + x + '"', value))
                value = ",".join(value)
                jsonString += key + ":[" + value + "], "
            else:
                [key,value] = line.split("=", 1)
                jsonString += '"' + key + '":"' + value + '", '

            line = f.readline().replace("\"", "\\\"").replace("\n", "")
        outString += jsonString[:-2] + '},\n'
    f.close()
        
outString = outString[:-2] + '\n]\n'
outFile = open("pictures.json","w")
outFile.write(outString)
outFile.close()

#!/bin/bash
find $1 -type f -print | grep -i '.picasa.ini' > picasa_files.txt;
./makeAlbumJSON.py < picasa_files.txt;
./makePictureJSON.py < picasa_files.txt;


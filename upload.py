#!/usr/bin/python3
import webbrowser
import requests
import json
import stat
import os

from pathlib import Path
from urllib.parse import urlencode

def main():
    pFiles   = findPicasaFiles()

    albums   = findAlbums(pFiles)
    print("Total of", len(albums), "albums.")
    pictures = findPictures(pFiles)
    print("Total of", len(pictures), "pictures.")
    
    tokens = get_tokens()
    access_token = tokens['access_token']

    ret =  postAlbums(albums, access_token)
    with open('.albums.json','w') as f:
        f.write(json.dumps(albums))
    if ret < 0:
        print("Try again later: albums didn't complete")
        return

    ret =  postPictures(pictures, albums, access_token)
    
    if ret < 0:
        with open('.pictures.json','w') as f:
            f.write(json.dumps(pictures))
        print("Try again later: pictures didn't complete")
        return
    print("done")

def findAlbums(picasaFiles):
    if os.path.exists(os.path.join('.', '.albums.json')):
        with open(os.path.join('.','.albums.json'),'r') as f:
            return json.load(f)
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
    
def postAlbums(albums, access_token):
    for token in albums:
        if "google_photos_id" not in albums[token] and "name" in albums[token]:
            r = postAlbum(albums[token]["name"], access_token)
            if r.status_code != requests.codes.ok:
                with open("error.log", "w") as f:
                    f.write(r.text)
                return -1
            
            albums[token]["google_photos_id"] = r.json()["id"]
    return 1

def postAlbum(album_name, access_token):
    base_url = "https://photoslibrary.googleapis.com/v1/albums"
    headers = {
        "Content-type" : "application/json",
        "Authorization" : "Bearer " + access_token,
    }
    body = {"album" : {"title" : album_name}}
    r = requests.post(url=base_url, headers=headers, json=body)
    return r

def postPictures(pictures, albums, access_token):
    for picture in pictures:
        r = postPicture(picture, access_token)
        if r.status_code != requests.codes.ok:
            with open("error.log", "w") as f:
                f.write(r.text)
            return -1
        google_token = r.text

        if "albums" not in picture:
            r = noAlbums(picture, google_token, access_token)
            if r.status_code != requests.codes.ok:
                with open("error.log", "w") as f:
                    f.write(r.text)
                return -1
            pictures.remove(picture)
        else:
            if postPictureAlbums(picture, albums, access_token, google_token) < 0:
                return -1
            pictures.remove(picture)
    return 1
            

def postPicture(picture, access_token):
    base_url = "https://photoslibrary.googleapis.com/v1/uploads"
    headers = {
        "Content-type" : "application/octet-stream",
        "Authorization" : "Bearer " + access_token,
        "X-Goog-Upload-File-Name" : os.path.basename(picture['path'])
    }
    body = open(picture['path'], 'rb')
    r = requests.post(url=base_url, headers=headers, data=body)
    print(picture["path"] + ": " + r.text)
    return r

def noAlbums(picture, google_token, access_token):
    base_url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
    headers = {
        "Content-type" : "application/json",
        "Authorization" : "Bearer " + access_token,
    }
    body = {
        "newMediaItems" : [{
            "description" : "",
            "simpleMediaItem" : {
                "uploadToken" : google_token
            }
        }]
    }
    r = requests.post(url=base_url, headers=headers, json=body)
    return r

def postPictureAlbums(picture, albums, access_token, google_token):
    if "albums" not in picture:
        return 1

    base_url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
    headers = {
        "Content-type" : "application/json",
        "Authorization" : "Bearer " + access_token,
    }
    for album in picture["albums"]:
        body = {
            "albumId" : albums[album]["google_photos_id"],
            "newMediaItems" : [{
                "description" : "",
                "simpleMediaItem" : {
                    "uploadToken" : google_token
                }
            }]
        }
        r = requests.post(url=base_url, headers=headers, json=body)
        if r.status_code != requests.codes.ok:
            with open("error.log", "w") as f:
                f.write(r.text)
            return -1
    return 1

def get_auth_code():
    
    with open('credentials.json',mode='r') as f:
       credentials = json.load(f)['installed']
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"

    authorization_code_req = {
        "scope" : (r"https://www.googleapis.com/auth/photoslibrary"),
        "response_type" : "code",  
        "client_id" : credentials["client_id"],
        "redirect_uri" : credentials["redirect_uris"][0],
    }

    req_string = base_url + "?%s" % urlencode(authorization_code_req)
    r = requests.get(req_string, allow_redirects=False)
    print(r)
    url = r.headers.get('location')
    webbrowser.open_new(url)

    authorization_code = input("\nAuthorization Code >>> ")
    print(authorization_code)
    print("well done")
    return authorization_code

def get_tokens():
    with open('credentials.json',mode='r') as f:
       credentials = json.load(f)['installed']
    base_url = "https://www.googleapis.com/oauth2/v4/token"

    access_token_req = {
        "code" : get_auth_code(),
        "client_id" : credentials["client_id"],
        "client_secret" : credentials['client_secret'],
        "redirect_uri" : credentials["redirect_uris"][0],
        "grant_type": "authorization_code",
    }
    content_length=len(urlencode(access_token_req))
    access_token_req['content-length'] = str(content_length)

    r = requests.post(base_url, data=access_token_req)
    print(r)
    data = json.loads(r.text)
    return data

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
            
    pic_list = []
    for k,v in pictures.items():
        v['path'] = k
        pic_list.append(v)
    return pic_list

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

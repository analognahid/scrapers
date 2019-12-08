
from fake_useragent import UserAgent
import requests
from requests.adapters import HTTPAdapter
import re
import sys, csv
import time
import math
import threading
import os
from os import listdir
from os.path import isfile, join
import pycurl
import sqlite3
from string import ascii_lowercase
import html
from sqlite3 import Error
import json


mainCount = 0
s = requests.Session()
s.mount('https', HTTPAdapter(max_retries=3))

dbDir = "/home/tigerit/Desktop/sqlite/celeb_database"
conn = sqlite3.connect(dbDir,timeout=35 )

startTime = time.time()

def printLog():
    global mainCount
    print(  'Active threads-->' ,threading.active_count() , ' row count -->', rowNum, ' main',mainCount , ' time ->>', math.floor(( time.time()-startTime)/(60*60)),'h', math.floor((( time.time()-startTime)/60)) %60,'m', math.floor(time.time()-startTime)%60,'s'  )


def createDirOnce(dir , userName ):
    if not os.path.exists(dir+userName):
        os.makedirs(dir+userName)

# ------------------------------------------------- theading



class grabLink (threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):
        global mainCount
        ua = UserAgent()
        header = {'User-Agent':str(ua.chrome)}

        
        userName =html.unescape(self.data[0])
        profilePhotoCount = 0
        selfCount = 0
        

        url = "http://www.zimbio.com/photos/"+userName
        try:
            
            
            htmlContent = requests.get(url, headers=header)
            slideIdRegex = 'data-share-url=\"http:\/\/www.zimbio.com\/photos\/.*\/.*\/(.*)" \/>'
            slideId = re.findall(slideIdRegex, htmlContent.content.decode('latin-1'))[0]
            # print(slideId)

            convertedUserName = userName.replace('+','')
            apiUrl = "http://www.zimbio.com/api/v1/cached/photostream?filters[]={}&type=solo&count=1000000&slide_id={}&offset=-6".format(convertedUserName,slideId)
            # print(apiUrl)

            response = requests.get(apiUrl, headers=header)

            jsonData = json.loads(response.content.decode('latin-1'))
            totalImages = int(jsonData['total_slides'])
     
            tConn = sqlite3.connect(dbDir,timeout=45 )
            tCur = tConn.cursor()
            dataArr = []
            for slide in jsonData['slides']:
                dataArr.append((userName,slide['img_url'],))
            mainCount+= len(dataArr)
            mQuery = "insert or ignore into zimbo_fine_image_links( user_name,link) values (?, ?)"
            tCur.executemany(mQuery , dataArr)
            tConn.commit()
            tCur.execute('update zimbio_peoples set is_done = 1 where user_name ="{}" '.format(self.data[0]))
            tConn.commit()
            tConn.close()
            htmlContent.connection.close()
            response.connection.close()

            # mainCount+=len(photoLinks)
            # selfCount+=len(photoLinks)


        except Exception as e:
            print("------------------------------------errrr------------------------->>>>>>>>>>>>")
            print (e, url)
            



# ------------------------------------------ threading



cur = conn.cursor()
cur.execute("""select user_name,name from zimbio_peoples where user_name <> '' order by user_name asc""")
 
rows = cur.fetchall()

conn.close()


rowNum = 0

for row in rows:
    rowNum +=1

    printLog()
    while threading.active_count()>9:
        time.sleep(.1)

    thread1 = grabLink(row+ ( rowNum, ))
    thread1.start()
    time.sleep(.1)
        

#  - - - - - - -- - - -- - - - -- - -- - - -

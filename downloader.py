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
import html
from sqlite3 import Error



mainCount = 0
perPageCount =20
s = requests.Session()
s.mount('https', HTTPAdapter(max_retries=3))

dbDir = "/home/tigerit/Desktop/sqlite/celeb_database"
conn = sqlite3.connect(dbDir,timeout=35 )
downloadDir ="/media/tigerit/Data/imdb_tsv/photos_depo/"
startTime = time.time()

def printLog():
    print(  'Active threads-->' ,threading.active_count() , ' row count -->', rowNum , ' time ->>', math.floor(( time.time()-startTime)/(60*60)),'h', math.floor((( time.time()-startTime)/60)) %60,'m', math.floor(time.time()-startTime)%60,'s'  )




def createDirOnce(dir , userName ):
    if not os.path.exists(dir+userName):
        os.makedirs(dir+userName)

# ------------------------------------------------- theading


class getCelebPhotos (threading.Thread):
    def __init__(self,data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):

        try:
            profileDirName = self.data[1]
            createDirOnce(downloadDir ,profileDirName )
            photoLinkPart = self.data[0][:-2]
            photoUrl = "http://celebs-place.com/gallery/{}/{}.jpg".format(self.data[1] ,photoLinkPart )
            photoName = photoLinkPart +'.jpg'

            fp = open(downloadDir +profileDirName+"/"+ photoName, "wb")
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, photoUrl)
            curl.setopt(pycurl.WRITEDATA, fp)
            curl.perform()
            curl.close()
            fp.close()

            newConn = sqlite3.connect(dbDir)
            nCur = newConn.cursor()
            nCur.execute('update celebs_place_fine_image_links set is_done =1 where link="'+self.data[0]+'"')
            newConn.commit()
            newConn.close()


        except Exception as e:
            print("------------------------------------errrr------------------------->>>>>>>>>>>>")
            print (e)
        





# ------------------------------------------ threading




cur = conn.cursor()
cur.execute("""select link,user_name from celebs_place_fine_image_links where is_done is null order by user_name""")
rows = cur.fetchall()
conn.close()


rowNum = 0

# for i in rows:print(i)


for row in rows:
        rowNum +=1
        
        printLog()
        while threading.active_count()>2:
            time.sleep(.25)

        thread1 = getCelebPhotos( row+(rowNum,))
        thread1.start()

        
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
from sqlite3 import Error
import shutil
from pathlib import Path

from fuzzywuzzy import fuzz
from fuzzywuzzy import process


s = requests.Session() 
s.mount('https', HTTPAdapter(max_retries=3))

dbDir = "/home/tigerit/Desktop/sqlite/celeb_database"
conn = sqlite3.connect(dbDir,timeout=25)
downloadDir ="/media/tigerit/Data/imdb_tsv/photos_depo/"



startTime = time.time()
def createDirOnce(dir , userName ):
    if not os.path.exists(dir+userName):
        os.makedirs(dir+userName)

def printLog():
    global rowNum
    print(  'Active threads-->' ,threading.active_count() , ' row count -->', rowNum , ' time ->>', math.floor(( time.time()-startTime)/(60*60)),'h', math.floor((( time.time()-startTime)/60)) %60,'m', math.floor(time.time()-startTime)%60,'s'  )

# ------------------------------------------------- theading


class grabImage (threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):
        global onlyNames
        try:
        
            # print(self.data)
            foundArr = process.extractOne(self.data[0], onlyNames, scorer=fuzz.token_sort_ratio)
            # print(self.data[0],foundArr)
            if foundArr[1]>=93:
                print(self.data[0] , foundArr)
                
                newConn = sqlite3.connect(dbDir,timeout=45)
                nCur = newConn.cursor()
                nCur.execute('update zimbio_peoples set is_match =1 where user_name="'+self.data[1]+'"')
                newConn.commit()
                newConn.close()


        except Exception as e:
            print("------------------------------------errrr------------------------->>>>>>>>>>>>")
            print (e)
        

# ------------------------------------------ threading


rowNum = 0

# select * from fan_pix_image_links where is_done is null

cur = conn.cursor()
# cur.execute("""select a.link, a.user_name, b.name from zimbo_fine_image_links as a left join  zimbio_peoples as b  on a.user_name=b.user_name where name is not null order by b.name """)

cur.execute("""select name, user_name from zimbio_peoples """)

rows = cur.fetchall()


cur.execute("""select * from celeb_clean_list""")
allCelebQ = cur.fetchall()

dArr = []
for row in allCelebQ:
   dArr.append([row[0], row[1], row[2]])
onlyNames = []
for i,row in enumerate(dArr):
    onlyNames.append(row[2])




for row in rows:
    rowNum +=1

    # print(row)

    # printLog()
    while threading.active_count()>20:
        time.sleep(.1)

    thread1 = grabImage(row+ ( rowNum, ))
    thread1.start()

        

#  - - - - - - -- - - -- - - - -- - -- - - -
conn.commit()
conn.close()
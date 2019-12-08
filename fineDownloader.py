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

        try:
            ua = UserAgent()
            header = {'User-Agent':str(ua.chrome)}
            profileDirName = self.data [0]
            photoName = self.data [1].split('+')[-1]
            
            filePath = Path(downloadDir +profileDirName+"/"+ photoName)

            if filePath.is_file():
                newConn = sqlite3.connect(dbDir,timeout=15)
                nCur = newConn.cursor()
                print(' already downloaded --> ',downloadDir +profileDirName+"/"+ photoName)
                Q ='update zimbo_fine_image_links set is_done =1 where link="'+self.data[1]+'"'
                nCur.execute(Q)
                newConn.commit()
                newConn.close()
                return
            
            
            createDirOnce(downloadDir ,profileDirName )
            url = self.data[1]


            print(url)

            # htmlContent = requests.get(url, headers=header)
            # regex = '<textarea id=\"share_link1\" onclick=\"this.select\(\)\;\" style=\'.*\' wrap="on" rows=".*" cols=".*"><img src="(.*?)" alt=\".*\"><br><a href=\".*\" target=\"_blank">.*<\/a>'
            # # another regex needed for pictures link.
            # photoLink = re.findall(regex, htmlContent.content.decode('latin-1'))
            
            # # print(photoLink)

            # if not len(photoLink):
            #     picRegex = '<a href=\".*\"><img width=\".*\" height=\".*\" src=\"(.*)\" alt=\".*\" \/><\/a>'
            #     photoLink = re.findall(picRegex, htmlContent.content.decode('latin-1'))

            # if(len(photoLink)):
            #     photoLink =photoLink [0]
                
            # else:
            #     print('--------------------------------------------- image not found--------------------------')
            #     print(url)
            #     return
            # htmlContent.connection.close()
            # photoName = ((photoLink.split('/').pop() ).split('full-').pop() ).replace('.' , '__'+self.photoId+'.')
            # userName = ((photoLink.split('/').pop() ).split('full-').pop()).split('.')[0]
            # print(  photoName)

            hackHeaders = ['User-Agent:'+str(ua.chrome)+'']
            
            print(downloadDir +profileDirName+"/"+ photoName , url)
            fp = open(downloadDir +profileDirName+"/"+ photoName, "wb")
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, fp)
            curl.setopt(pycurl.HTTPHEADER,hackHeaders )
            curl.perform()
            curl.close()
            fp.close()
            
            # # update db
            newConn = sqlite3.connect(dbDir,timeout=15)
            nCur = newConn.cursor()
            nCur.execute('update zimbo_fine_image_links set is_done =1 where link="'+self.data[1]+'"')
            newConn.commit()
            newConn.close()



        except Exception as e:
            print("------------------------------------errrr------------------------->>>>>>>>>>>>")
            print (e, url)
        

# ------------------------------------------ threading


rowNum = 0

# select * from fan_pix_image_links where is_done is null

cur = conn.cursor()

cur.execute("""select zimbo_fine_image_links.user_name, zimbo_fine_image_links.link from zimbo_fine_image_links left join zimbio_peoples on zimbo_fine_image_links.user_name=zimbio_peoples.user_name 
where zimbio_peoples.is_match=1 and zimbo_fine_image_links.is_done is null """)

rows = cur.fetchall()

print("download left ", len(rows))
for row in rows:
    rowNum +=1

    print(row)

    # printLog()
    while threading.active_count()>2:
        time.sleep(.1)

    thread1 = grabImage(row+ ( rowNum, ))
    thread1.start()

    time.sleep(.1)

        

#  - - - - - - -- - - -- - - - -- - -- - - -
conn.commit()
conn.close()
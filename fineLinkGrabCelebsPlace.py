# <a href=\"\/photos\/[name](.*)\/\" class=\"mbox\">

# <span class=\"btn btn-default\"><i class=\"fa fa-camera"><\/i> Photo.? \[(.*)\]<\/span>


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



mainCount = 0
perPageCount =20
s = requests.Session()
s.mount('https', HTTPAdapter(max_retries=3))

dir = "/home/tigerit/Desktop/sqlite/"
conn = sqlite3.connect(dir+ 'celeb_database',timeout=35 )

startTime = time.time()

def printLog():
    print(  'Active threads-->' ,threading.active_count() , ' row count -->', rowNum , ' time ->>', math.floor(( time.time()-startTime)/(60*60)),'h', math.floor((( time.time()-startTime)/60)) %60,'m', math.floor(time.time()-startTime)%60,'s'  )


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

        
        userName = self.data[0]
        profilePhotoCount = 0
        selfCount = 0
        for i in range(1, 3000 ):
            # url = f"http://fanpix.famousfix.com{self.data[2]}?pageno={i}"
            url = "http://celebs-place.com/photos/{}/page{}/".format(userName ,  str(i))
            htmlText = ''
            try:
                
                htmlContent = requests.get(url, headers=header)
                htmlText = htmlContent.content.decode('latin-1')
                if(i==1):
                    countRegex = '<p>Check out photogallery with (.*?) '
                    profilePhotoCount = re.findall(countRegex, htmlText )
                    if not len(profilePhotoCount):
                        break
                    profilePhotoCount = int(profilePhotoCount[0])
                    htmlText = htmlText.split('Check out photogallery with')[-1]
                    # print(profilePhotoCount)

                linksRegex = '<img alt=\".*\" src="\/gallery\/{}\/(.*)\.jpg\" class=\"pic\">'.format(userName)
                
                photoLinks = re.findall(linksRegex, htmlText)
                
                # linkData = [] 
                # for link in photoLinks:
                #     # fullLink  ="http://celebs-place.com/gallery/{}/{}.jpg".format(userName ,link[:-2]) 
                #     linkData.append((link , userName) )
                

    
                # print(len(linkData), url)
                tConn = sqlite3.connect(dir+ 'celeb_database',timeout=45 )
                tCur = tConn.cursor()
                # mQuery = 'INSERT OR IGNORE INTO celebs_place_fine_image_links(link, user_name ) VALUES(?,?)'
                for link in photoLinks:
                    # fullLink  ="http://celebs-place.com/gallery/{}/{}.jpg".format(userName ,link[:-2]) 
                    q="INSERT INTO test(link, user_name ) VALUES('{}','{}')".format(link , userName)
                    tCur.execute(q)
                    tConn.commit()
                tConn.close()
                htmlContent.connection.close()
                mainCount+=len(photoLinks)
                selfCount+=len(photoLinks)
                if len(photoLinks)<20:
                    print(profilePhotoCount , selfCount,mainCount)
                    break

                if profilePhotoCount%20 == 0 and i>= math.ceil(profilePhotoCount/ perPageCount):
                    print(profilePhotoCount , selfCount ,mainCount)
                    break
                if i> (math.floor(profilePhotoCount/ perPageCount)+1) :
                    print(profilePhotoCount , selfCount ,mainCount)
                    break
                # print(photoLinks)
            except Exception as e:
                print("------------------------------------errrr------------------------->>>>>>>>>>>>")
                print (e, url)
            



# ------------------------------------------ threading



cur = conn.cursor()
cur.execute("""select user_name from celebs_place_profiles where user_name <> '' order by user_name asc""")
 
rows = cur.fetchall()

conn.close()
# for row in rows:
#     print(row)

rowNum = 0

for row in rows:
    rowNum +=1

    printLog()
    while threading.active_count()>15:
        time.sleep(.1)

    thread1 = grabLink(row+ ( rowNum, ))
    thread1.start()
    time.sleep(.1)
        

#  - - - - - - -- - - -- - - - -- - -- - - -

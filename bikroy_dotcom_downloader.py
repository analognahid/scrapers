# importing the requests library
from fake_useragent import UserAgent
import requests
from requests.adapters import HTTPAdapter
import re
import sys, csv
import time
import threading
import sqlite3
from string import ascii_uppercase
import html
import json
from random import shuffle
import pymysql.cursors


connection = pymysql.connect(host='localhost',
                             user='root',
                             password='tigerit',
                             db='bikroy',
                            #  charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor =  connection.cursor() 

headers = {
    'cache-control': "no-cache",
    }

class getItems (threading.Thread):
    def __init__(self,data):
        threading.Thread.__init__(self)
        self.data = data
        print (self.data)

    def run(self):

        url = "https://bikroy.com/en/ads/bangladesh/cars?page="+ str(self.data)
    
        htmlContent = requests.request("GET", url, headers=headers)

        regex ="\"priceCurrency\":[\W]\"Tk\",[\W][\t]\"url\":[\W]\"(.*)\"[\W]"

        links = re.findall(regex, htmlContent.content.decode('utf-8'))
        htmlContent.connection.close()

        q="INSERT  ignore INTO item( link ) VALUES(%s)"
        cursor.executemany(q , links)

        connection.commit()
# ------------------------------------------ threading



start = 1
end   = 317
# 317
for i in range(start,end):

    while threading.active_count()>1:
        time.sleep(.1)
    thread1 = getItems( i)
    thread1.start()

    
connection.close()
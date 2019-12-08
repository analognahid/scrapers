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
    'user-agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64;en; rv:5.0) Gecko/20110619 Firefox/5.0"
    }

class getPics (threading.Thread):
    def __init__(self,data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):


        url = self.data[1]
        print(self.data)

        while True:
            try:
                # defining the api-endpoint 

                htmlContent = requests.request("GET", url, headers=headers)

                # <dl><dt>Condition:</dt><dd>Reconditioned</dd>
                if htmlContent.content.decode('utf-8').find("<dl><dt>Condition:</dt><dd>Reconditioned</dd>") >= 0:
                    print("Reconditioned -----------------------------")
                    uq = "update item set done =TRUE where id = {}".format(self.data[0])
                    cursor.execute(uq)
                    connection.commit()

                else:
                    regex ="fitted.jpg 1x, \/\/(.*?)fitted.jpg 1.3x\" class=\"is-pre-load\""
                    links = re.findall(regex, htmlContent.content.decode('utf-8'))
                    htmlContent.connection.close()
                    
                    temp =  [  (i,self.data[0],) for i in links ]
            
                    q="INSERT  INTO images( url,item_id ) VALUES(%s , %s)"
                    cursor.executemany(q , temp)
                    connection.commit()

                    uq = "update item set done =TRUE where id = {}".format(self.data[0])
                    cursor.execute(uq)
                    connection.commit()

                break


            except Exception as e:
                print("------------------------------------errrr------------------------->>>>>>>>>>>>")

        
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                time.sleep(3*1000)
                # nConn.close()



# ------------------------------------------ threading

fetchQuery = "select * from item where done is null or done is not true order by id"


cursor.execute(fetchQuery)
rows = cursor.fetchall()


rows_tuple = [tuple(d.values()) for d in rows]


rowCount = 0
for row in rows_tuple:
    rowCount+=1

    while threading.active_count()>1:
        time.sleep(1)
    thread1 = getPics( row+(rowCount,))
    thread1.start()

    
connection.close()
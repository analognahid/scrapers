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

dir = "/home/tigerit/Desktop/sqlite/"
conn = sqlite3.connect(dir+ 'celeb_database')
c = conn.cursor()

s = requests.Session()
s.mount('https', HTTPAdapter(max_retries=3))

ua = UserAgent()
header = {'User-Agent':str(ua.chrome)}

for char in ascii_uppercase:

    url = "http://celebs-place.com/photos/people-"+char+".html"

    print(url)
    htmlContent = requests.get(url, headers=header)
    
    nameRegex = '<span class=\"name\">(.*)<\/span>'
    userNameRegex ='<a href="\/photos\/(.*)\/" class="mbox">'

    names = re.findall(nameRegex,  htmlContent.content.decode('latin-1'))
    userNames = re.findall(userNameRegex,  htmlContent.content.decode('latin-1'))
    
    dataArr =[]
    for i in range (0, len(names)-1):
        print(names[i], userNames[i])
        dataArr.append((names[i], userNames[i],))

    manyQuery ='INSERT OR IGNORE INTO celebs_place_profiles(name, user_name) VALUES(?,?)'
    c.executemany(manyQuery, dataArr)



    # if not len(arr):
    #     break

    # for row in arr:
    #     # c.execute(  "INSERT INTO fan_pix VALUES ('" +row[1]+ "',"+row[2]+","+row[0]+")"  )
    #     name = html.unescape (row[1])
    #     name = name.replace('"',"'")
    #     # name = name.replace("'","\'")
    #     query = f'INSERT OR IGNORE INTO fan_pix VALUES("{name}",{row[2].replace(",","")},"{row[0]}"  )'
    #     print(query)
    #     c.execute(query)
            
#  - - - - - - -- - - -- - - - -- - -- - - -
conn.commit()
conn.close()






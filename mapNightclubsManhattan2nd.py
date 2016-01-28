get_ipython().magic(u'matplotlib inline')
import json
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from urllib2 import Request, urlopen, URLError
import requests
import pymysql as mdb
#from mpl_toolkits.basemap import basemap
from BeautifulSoup import BeautifulSoup
import xml.sax
import copy
import networkx as nx
from gisfile2 import download_osm, read_osm

areas=['Gramercy', 'HellsKitchen', 'Koreatown', 'LowerEastSide', 'LowerManhattan', 'MeatpackingDistrict', 'Midtown', 'Noho', 'NolitaLittleItaly', 'Soho', 'TimesSquare',
      'Tribeca', 'UnionSquare', 'UpperWastSide', 'UpperWastSide' , 'WashingtonHeights', 'WestVillage']

fullManhattan ={}
for i in range(len(areas)):
    with open('NightlifeManhattan'+areas[i]+'.json') as data_file:    
       fullManhattan['data'+areas[i]] = json.load(data_file)
test_data = []
for j in range(len(areas)):
    for i in range(len(fullManhattan['data'+areas[j]])):
        test_data.append((fullManhattan['data'+areas[j]]['businesses'][i+1]['name'],
                          fullManhattan['dataMidtown']['businesses'][i]['location']['display_address'],
                         fullManhattan['data'+areas[j]]['businesses'][i+1]['location']['coordinate']['latitude'],
                        fullManhattan['data'+areas[j]]['businesses'][i+1]['location']['coordinate']['longitude'],
                        fullManhattan['data'+areas[j]]['businesses'][i+1]['rating'],
                        fullManhattan['data'+areas[1]]['businesses'][i+1]['review_count'],
                         fullManhattan['data'+areas[1]]['businesses'][i+1]['snippet_text']))
df = pd.DataFrame(test_data)
df.columns = ['name','display_address','latitude', 'longitude', 'rating', 'review count','snippet text']
df    
# the API from google to extract inofrmations from google
YOUR_API_KEY = 'AIzaSyAebphqCTunUFb9LhcNXFf51djHmwbzDBo'
# to get the informations about the night clubs in Manhattan
link=[]
for i in range(len(areas)):  
    link.append('https://maps.googleapis.com/maps/api/place/textsearch/json?query=nightlife+in+'+areas[i]+'&key='+ YOUR_API_KEY)
    #link = 'https://www.google.com/webhp?sourceid=chrome-instant&ion=1&espv=2&es_th=1&ie=UTF-8#q=cinema+new+york&rflfq=1&tbm=lcl&key='+ YOUR_API_KEY
    request = Request(link[i])

    try:
        response = urlopen(request)
        kittens = response.read()
        #print kittens[559:1000]
    except URLError, e:
             print 'No kittez. Got an error code:', e  
google_map_1 = BeautifulSoup(urlopen(link[1]).read())
google_manhattan = {}
google_manhattan['data_manhattan_from_google']=google_map_1
gjson = json.loads(google_map_1.contents[0])
import pandas as pd

google_data = []
for i in range(len(gjson['results'])):
    google_data.append((gjson['results'][i]['name'],
        gjson['results'][i]['formatted_address'],
        gjson['results'][i]['geometry']['location']['lat'],
        gjson['results'][i]['geometry']['location']['lng'],
        gjson['results'][i]['rating'],
        gjson['results'][i]['types'] ))
    
df_google = pd.DataFrame(google_data)
df_google.columns = ['name','display_address','latitude', 'longitude', 'rating', 'Type']
df.google.to_csv('cleaneGoogleData.csv')
df_google
db = df_google.to_sql(name='Nightclubs', con=con, if_exists = 'append', index=False, flavor='mysql')

db
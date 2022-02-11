import psycopg2
import re
import requests
import urllib
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd

def setUpDB(command, url):
    """ create tables in the PostgreSQL database"""
    
    try:        
        # connect to the PostgreSQL server
        conn = psycopg2.connect(url, sslmode='require')
        cur = conn.cursor()
        
        # create table one by one
        cur.execute(command)
        
        # close communication with the PostgreSQL database server
        cur.close()
        
        # commit the changes
        conn.commit()
        conn.close()
        print('done')
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
def getData(command, url):    
    conn = psycopg2.connect(url, sslmode='require')
    
    try:
        df = pd.read_sql(command, conn)
        if conn is not None:
            conn.close()
        
        return df
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

# def getLinks(string):
#     regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
#     allLinks = re.findall(regex, string)
    
#     if len(allLinks) > 1:
#         result = ''
        
#         for i in allLinks:
#             result += i[0] + ';'
        
#         return result
    
#     elif len(allLinks) == 1: return allLinks[0]
#     else: return ''

def getLinks(string):
    urls = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", string)
    links = ''
    
    for url in urls:
        try:
            opener = urllib.request.build_opener()
            request = urllib.request.Request(url)
            response = opener.open(request)
            actual_url = response.geturl()
                        
            if '](' in actual_url:
                actual_url = actual_url.split('](')[0]
            
            links += actual_url + ';'
            
            
        except:
            if '](' in url:
                url = url.split('](')[0]
            
            links += url + ';'

    return links

def getURLfromList(url):
    if ';' in url:
        url = url.split(';')[:-1]
        result = []
        
        for i in url:
            result.append(urlparse(i).hostname)
            
        return result
    
    else:
        return ''
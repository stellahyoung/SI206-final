import sqlite3
import re
import os
import unittest
import json
import requests
import numpy as np
import scipy.stats
import statistics
import math
import matplotlib.pyplot as plt 
from bs4 import BeautifulSoup


# Team Name: Elizabeth + Stella
# Group Members: Stella Young ELizabeth Kim

# Create database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# Get concert data in json
def concert_web():
    web_data = {}
    
    url = "https://www.songkick.com/leaderboards/popular_artists"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    result = soup.find('table')
    row = result.find_all('tr')
    
    for i in range(1, len(row)):
        content = row[i].find('td', class_ = 'concert-count')
        for data in content:
            #print(content)
            #print(data)
            # print(countries[i].select("td")[1])
            artist = row[i].select("td")[2].text
            web_data[artist.strip()] = str(data.strip())

    return concert_web

# Create Concerts table
def create_concert_table(concert_web, cur, conn):
    data_key = list(concert_web.keys())
    print(data_key)
    print(concert_web)

    cur.execute("CREATE TABLE Grammy (Artist TEXT PRIMARY KEY, Concerts INT)")
    for i in data_key:
        cur.execute("INSERT INTO Grammy (Artist, Concerts) VALUES (?,?)",(i, concert_web[i]))
    conn.commit()

#Taylor Swift Specific
#def spotify_api():
#    url = 'https://api.spotify.com/v1/artists/06HL4z0CvFAxyc27GXpf02'
#    token = 'BQBZWbhyAYpXwcCXnFjc8o3fg_zNcuLpQ4W9Dkkc2qHJqt2ht1Yuaipcd9wiZ8J4YIIm_xXYy_WpQ1bwnf5if9t2QNHrgdRITeF3JlIbkjKYP4HemYK5a5CSJCORmeQNNtaP23Yu3DhSa9Cj4k_H3qHQtH5eZvOy4VTZosqczr_rcHRxQgXzBBS71QVLqjH9zRHioWc'
#    response = requests.get(url, headers = {"Authorization": f"Bearer {token}"})
 #   data = response.json()
 #   print(data)
 #   return data


#takes in list of artist_ids (Taylor Swift, Ariana Grande)

artists_info = {}

def spotify_api(artists_info):
    
    for id in artists_info.keys():
        url = ('https://api.spotify.com/v1/artists/' + id)
        #token = 'BQBZWbhyAYpXwcCXnFjc8o3fg_zNcuLpQ4W9Dkkc2qHJqt2ht1Yuaipcd9wiZ8J4YIIm_xXYy_WpQ1bwnf5if9t2QNHrgdRITeF3JlIbkjKYP4HemYK5a5CSJCORmeQNNtaP23Yu3DhSa9Cj4k_H3qHQtH5eZvOy4VTZosqczr_rcHRxQgXzBBS71QVLqjH9zRHioWc'
        token = artists_info.get(id)
        response = requests.get(url, headers = {"Authorization": f"Bearer {token}"})
        data = response.json()
        print(data)
    return data




spotify_api({'06HL4z0CvFAxyc27GXpf02': 'BQBZWbhyAYpXwcCXnFjc8o3fg_zNcuLpQ4W9Dkkc2qHJqt2ht1Yuaipcd9wiZ8J4YIIm_xXYy_WpQ1bwnf5if9t2QNHrgdRITeF3JlIbkjKYP4HemYK5a5CSJCORmeQNNtaP23Yu3DhSa9Cj4k_H3qHQtH5eZvOy4VTZosqczr_rcHRxQgXzBBS71QVLqjH9zRHioWc', 
'66CXWjxzNUsdJxJ2JdwvnR':'BQAlSp6WZ9HeZk7AfxbuqX45kFNtOlDi35Pug_fN9jPMJbrR2E1Evr39jTI2MwczpBHBX-xISIJpitTqL09QpIz1PoleiYQyDJz6qgTdLh6JzEQSCtJmyHU-AsCtfHIMAYhXvD1wOquh7ne2IelCHUHlg99YklzhSiA4cVVFBfwKXv1mvN4xiSjsvcP1m3YPmyvh1cQ'}
)
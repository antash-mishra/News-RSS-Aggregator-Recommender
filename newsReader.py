from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import xml.etree.ElementTree as ET
#from tfidf_recommendation import TFIDF_based_model
import sqlite3
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import numpy as np
import xml.dom.minidom
import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root, width=200, height=100)
canvas.pack()

def fetch_rss_feed(feed_url):
    response = requests.get(feed_url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch RSS feed: {response}")
        return None

def parse_and_insert(data, feed_type): 
    soup = BeautifulSoup(data, 'xml') if data is not None else ''

    feed_datas = []

    for item in soup.find_all('item'):
        #print(item.find('description').text)
        title = item.find('title').text.strip() if item.find('title') is not None else ''

        description_element = item.find('description')
        description = description_element.text if description_element is not None else ''

        link = item.find('link').text.strip() if item.find('link') is not None else ''
        pubDate = item.find('pubDate').text.strip() if item.find('pubDate') is not None else ''
        imgLink = item.find('enclosure')['url'] if item.find('enclosure') is not None else (item.find('media:content')['url'] if item.find('media:content') is not None else (item.find('media:thumbnail')['url'] if item.find('media:thumbnail') is not None else ''))
    
        entry_dict = {
            'title': title,
            'description': description,
            'link': link,
            'pubDate': pubDate,
            'imgLink': imgLink,
            'feedType': feed_type
        }
        
        feed_datas.append(entry_dict)
    return feed_datas


def interact_database_table(entries):
    conn = sqlite3.connect(r'C:\Users\Antash\Desktop\news Agg Recsys\rss_data.db')
    
    cursor = conn.cursor()
    print(cursor)
    for entry in entries:
        cursor.execute('''
            INSERT OR IGNORE INTO recent_news (title, description, link, pubDate,imgLink, feedType)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            entry.get('title', ''),
            entry.get('description', ''),
            entry.get('link', ''),
            entry.get('pubDate', ''),
            entry.get('imgLink', ''),
            entry.get('feedType', '')
             ))
        
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect('rss_data.db')
    c = conn.cursor()
    c.execute('''
            SELECT 
              coalesce(title, '') as title, 
              coalesce(description, '') as description, 
              coalesce(link,'') as link, 
              coalesce(pubDate, '') as pubDate, 
              coalesce(imgLink, '') as imgLink, 
              coalesce(feedType, '') as feedType 
            FROM recent_news
        ''')
    data = c.fetchall()
    conn.close()
    return data

    
def rss_data_in_table(url, rss_type):
    xml_data = fetch_rss_feed(url)
    rss_entries = parse_and_insert(xml_data, rss_type)
    interact_database_table(entries=rss_entries)


def add_url():
    
    urls = [
        'https://timesofindia.indiatimes.com/rssfeedmostrecent.cms', 
        'https://timesofindia.indiatimes.com/rssfeeds/4719148.cms',
        'https://rss.nytimes.com/services/xml/rss/nyt/US.xml'
    ]
    
    feedType = ''

    for url in urls:
        print(url) 
        rss_data_in_table(url, feedType)
    return urls
    
# @app.route('/data')
def get_data_json():
    data = get_data()
    columns = ('title', 'description', 'link', 'pubDate', 'imgLink', 'feedType')
    json_data = [{columns[i]: row[i] for i in range(len(columns))} for row in data]

    return jsonify(json_data)

# name = "50 Worst Habits For Belly Fat"

# ind=df2[df2['Title']==name].index[0]
# dd=TFIDF_based_model(ind, 100)
# dd.head(10)


if __name__ == "__main__":
    # app.run(debug=True)
    add_url()


    #rss_feed_url = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    #rss_feed_url = "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms"
    #rss_feed_url = "https://timesofindia.indiatimes.com/rssfeeds/54829575.cms"
    #create_database()
    # xml_data = fetch_rss_feed(rss_feed_url)
    # rss_entries = parse_and_insert(xml_data)
    # interact_database_table(rss_entries)
    # rss_type = "Sports"
    # rss_data_in_table(rss_feed_url, rss_type=rss_type)
        
    
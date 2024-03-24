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




hostName = "localhost"
serverPort = 8080

app = Flask(__name__)


def create_database():
    conn = sqlite3.connect('rss_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS toi_recent_popular_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            link TEXT,
            pubDate TEXT,
            imgLink TEXT,
            feedType TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_database()

def fetch_rss_feed(feed_url):
    response = requests.get(feed_url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch RSS feed: {response}")
        return None
    
def get_first_image_url(url, news_title):
    # Send a GET request to the website
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the first <img> tag in the HTML
        images = soup.find_all('img')      
        for img in images:
            if img.get('alt', '').strip() == news_title.strip() or img.get('alt', '').strip() != "WIRED":
                print("Alt: " , img.get('alt', '').strip())
                img_src = img.get('src')
                return img_src
            elif len(img.get('title', '').strip()) != 0:
                print("Title: ", img.get('title', '').strip())
                img_src = img.get('src')
                return img_src
            elif img.get('fetchpriority') == "high":
                img_src = img.get('src')
                return img_src
            
    else:
        print("Failed to retrieve webpage:", response.status_code)
        return None

def parse_and_insert(data, feed_type): 
    soup = BeautifulSoup(data, 'xml') if data is not None else ''

    feed_datas = []

    for item in soup.find_all('item'):
        #print(item.find('description').text)
        print("Hello World", item.find('title'), item.find('media:thumbnail')['url'] if item.find('media:thumbnail') is not None else '')
        title = item.find('title').text.strip() if item.find('title') is not None else ''

        description_element = item.find('description')
        description = description_element.text if description_element is not None else ''

        link = item.find('link').text.strip() if item.find('link') is not None else ''
        pubDate = item.find('pubDate').text.strip() if item.find('pubDate') is not None else ''
        imgLink = (item.find('enclosure').get('url', '') 
       if item.find('enclosure') is not None 
       else (item.find('media:content').get('url', '') 
             if item.find('media:content') is not None 
             else (item.find('media:thumbnail').get('url', '') 
                   if item.find('media:thumbnail') is not None 
                   else '')))

        imageLink = get_first_image_url(link, title)


        entry_dict = {
            'title': title,
            'description': description,
            'link': link,
            'pubDate': pubDate,
            'imgLink': imgLink,
            'feedType': feed_type,
            'imageLinkNew': imageLink
        }
        
        feed_datas.append(entry_dict)
    return feed_datas


def interact_link_table(link, feed_type):
    conn = sqlite3.connect('rss_data.db')
    
    cursor = conn.cursor()
    print(cursor)
    cursor.execute('''
        INSERT OR IGNORE INTO dm_link (link, feedType)
        VALUES (?, ?)
    ''', (
        link,
        feed_type
        ))
        
    conn.commit()
    conn.close()


def interact_database_table(entries):
    conn = sqlite3.connect(r'C:\Users\Antash\Desktop\news Agg Recsys\rss_data.db')
    
    cursor = conn.cursor()
    print(cursor)
    for entry in entries:

        cursor.execute('''
            INSERT OR IGNORE INTO test (title, description, link, pubDate,imgLink, feedType, imageLinkNew)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.get('title', ''),
            entry.get('description', ''),
            entry.get('link', ''),
            entry.get('pubDate', ''),
            entry.get('imgLink', ''),
            entry.get('feedType', ''),
            entry.get('imageLinkNew', '')
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
              coalesce(feedType, '') as feedType,
              coalesce(imageLinkNew, '') as imageLink
            FROM test
        ''')
    data = c.fetchall()
    conn.close()
    return data

def get_link_data():
    conn = sqlite3.connect('rss_data.db')
    c = conn.cursor()
    c.execute('''
            SELECT 
              coalesce(link, '') as link, 
              coalesce(feedType, '') as feedType 
            FROM dm_link
        ''')
    data = c.fetchall()
    conn.close()
    return data

    
def rss_data_in_table(url, rss_type):
    xml_data = fetch_rss_feed(url)
    rss_entries = parse_and_insert(xml_data, rss_type)
    interact_database_table(entries=rss_entries)


@app.route('/', methods= ['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/add_url', methods=['POST'])
def add_url():
    if request.method == 'POST':
        url = request.form['url']
        feedType = request.form['feedType']
        print(url)

        interact_link_table(url, feedType)
        links = get_link_data()
        for link in links:
            
            url = link[0]
            feedType = link[1]
            print(url, feedType)
            rss_data_in_table(url, feedType)
        
        return redirect(url_for('index'))
    
@app.route('/data')
def get_data_json():
    data = get_data()
    columns = ('title', 'description', 'link', 'pubDate', 'imgLink', 'feedType', 'imageLink')
    json_data = [{columns[i]: row[i] for i in range(len(columns))} for row in data]

    # return jsonify(json_data)
    print(json_data)
    return render_template('news.html', data=json_data)

# name = "50 Worst Habits For Belly Fat"

# ind=df2[df2['Title']==name].index[0]
# dd=TFIDF_based_model(ind, 100)
# dd.head(10)


if __name__ == "__main__":
    app.run(debug=True)
    #rss_feed_url = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    #rss_feed_url = "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms"
    #rss_feed_url = "https://timesofindia.indiatimes.com/rssfeeds/54829575.cms"
    #create_database()
    # xml_data = fetch_rss_feed(rss_feed_url)
    # rss_entries = parse_and_insert(xml_data)
    # interact_database_table(rss_entries)
    # rss_type = "Sports"
    # rss_data_in_table(rss_feed_url, rss_type=rss_type)
        
    
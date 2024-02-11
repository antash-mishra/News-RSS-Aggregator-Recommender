from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import xml.etree.ElementTree as ET
from tfidf_recommendation import TFIDF_based_model



hostName = "localhost"
serverPort = 8080

def fetch_rss_feed(feed_url):
    response = requests.get(feed_url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch RSS feed.")
        return None

# name = "50 Worst Habits For Belly Fat"

# ind=df2[df2['Title']==name].index[0]
# dd=TFIDF_based_model(ind, 100)
# dd.head(10)


if __name__ == "__main__":
    rss_feed_url = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"

    xml_data = fetch_rss_feed(rss_feed_url)

    print(xml_data)

    
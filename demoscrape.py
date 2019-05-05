import json
import os
import requests
from lxml import etree

CACHE_FILE = "scrape.cache.json"

URL = "https://www.epa.gov/ground-water-and-drinking-water/national-primary-drinking-water-regulations"

def get_url(data, url):
    if url not in data['url']:
        print("Fetching '%s'" % url)
        res = requests.get(url)
        data['url'][url] = res.text
    return data['url'][url]


def do_stuff(data):
    html = get_url(data, URL)

    sub_urls = get_subs_recursive(data, html)

def get_subs_recursive(html):

    parser = etree.HTMLParser()
    tree = etree.parse(html, parser)
    return tree

def main():
    if not os.path.exists(CACHE_FILE):
        data = {'url':{}}
    else:
        data = json.load(open(CACHE_FILE))
    try:
        do_stuff(data)
    finally:
        json.dump(data, open(CACHE_FILE, 'w'))

if __name__ == "__main__":
    main()

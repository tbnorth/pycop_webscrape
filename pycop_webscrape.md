# Web-scraping in Python

https://tbnorth.github.io/pycop_webscrape/


# Overview

 - What is web-scraping
 - Why you shouldn't need to do it
 - Why you shouldn't do it
 - How to do it
   - Getting data
   - Parsing data


# What is web-scraping

- Automated collection of data from web pages designed to
  be read by people.
- Using software to fetch web content (based on URLs) and
  create structured data from the HTML etc. returned.



## Why you shouldn't need to do it

 - Data rich sites should provide links to download data
 - AND / OR
 - An API to get data via web requests (REST etc.)

`http://example.com/api/v3/get_rainfall?huc=08003&fmt=json`


# Why you shouldn't do it

 - Is the data available for sale, and if so, is it reasonable to
   bypass that?
 - Web access logs will probably be logging your network
   address, is that going to cause concern / misperception?
 - Too many requests per second / hour / day maybe (temporarily)
   block your access.



## Why you'll wish you weren't doing it

 - Hand edited sites lack consistency
 - `<!-- #BeginEditable "body" -->`
 - Even generated sites may have multiple generations
   of output format


# Parsing content

 - Web scraping scripts often specific to a single web site
 - Often a static and / or legacy website that won't be changing
 - So the code needn't be perfect, it may only be run once
 - Only needs to work for the content that is on the site, no need
   to worry about cases that don't occur
 


# Getting content

 - Browser tools for inspecting content
 - "Hidden" data, e.g. coordinates [on a map](https://www.skinnyski.com/trails/ski/listings.asp?region=ne-mn)
 - Or links [in an image](https://www.epa.gov/wqs-tech/state-specific-water-quality-standards-effective-under-clean-water-act-cwa)
 - Multi-level retrieval (contents listing, then data)
 - Tables [linked from a list](https://www.epa.gov/ground-water-and-drinking-water/national-primary-drinking-water-regulations)
 - Binary things (images, PDFs)



## urllib(s)

 - All return HTML page content as a string / bytes
 - Python 2 urllib - takes URL string
 - Pyhton 2 urllib2 - builds request (headers, auth.)
 - Python 3 urllib.request - like urllib2 above
 - Python 3 recommends 3rd party `requests` library



## requests

 - http://docs.python-requests.org/
 - Requests: HTTP for Humans (TM)
 - Requests is the only Non-GMO HTTP library for Python, safe for human consumption
 - Requests 2 works with Python 3.x, Requests 3 is coming soon
 - Better for handling multi stage log in (session)



## Authentication

For older, less common "pop-up" authentication:

```python
s = requests.Session()
s.auth = ('user', 'pass')
url = "https://example.com/protected_page.html"
s.get(url)
data['urls'][url] = s.text
```
Site login style authentication is doable but more
site specific.


# Caching content

 - During development of a scraping script, you'll need the
   content of a particular URL many times
 - That content probably won't change, or the changes will
   be unimportant for development
 - Caching the URL's content locally will make development
   much faster
 - And minimize "too many requests per minute" lock outs



## Persistent dict
```python
import json, os
CACHE_FILE = "scrape.cache.json"

def main():
    if not os.path.exists(CACHE_FILE):
        data = {}
    else:
        data = json.load(open(CACHE_FILE))
    try:
        do_stuff(data)
    finally:
        json.dump(data, open(CACHE_FILE, 'w'))
```



## Don't use the top level

```python
{
    "http://www...": "<html><head><title>XKCD - 12...",
    "http://www...": "<html><head><title>XKCD - 13...",
    "http://www...": "<html><head><title>XKCD - 14...",
    ...
}
```

```python
{
    'last_run': "Sat 05/04/2019", 
    'url: {
        "http://www...": "<html><head><title>XKCD - 12...",
        "http://www...": "<html><head><title>XKCD - 13...",
        "http://www...": "<html><head><title>XKCD - 14...",
        ...
    }
}
```



## Don't use the second level either...

```python
{
    'last_run': "Sat 05/04/2019", 
    'url: {
        "http://www...": {
            'last_fetch': "2019-04-04 13:42:23",
            'content': "<html><head><title>XKCD - 12...",
        }
        "http://www...": {
            'last_fetch': "2019-04-04 13:42:23",
            'content': "<html><head><title>XKCD - 13...",
        }
        ...
    }
}
```

(Unless you want to)



## First time set up of persistent dict

```python
import json, os, time
CACHE_FILE = "scrape.cache.json"

def main():
    if not os.path.exists(CACHE_FILE):
        data = {'last_run': time.asctime(), 'url':{}}
    else:
        data = json.load(open(CACHE_FILE))
    try:
        do_stuff(data)
    finally:
        json.dump(data, open(CACHE_FILE, 'w'))
```


# Parsing content and extracting data

Whatever works. 



## Simple text parsing

```html
<h2>Contries</h2>
<div>Country: New Zealand</div>
<div>Population: 4321321</div>
<div>Sheep: 12,000,000</div>
<hr/>
<div>Country: India</div>
<div>Population: 1,339,000,000</div>
<div>Sheep: Unknown</div>
```



## Simple text parsing

```python
result = {}
for line in data['url'][url].split('\n'):
    line = line.replace("<div>", "").replace("</div>", "")
    if "Country" in line:  # Country: New Zealand
        country = line.split(None, 1)[1]
    if "Population" in line:  # Population: 4321321
        result[country] = int(line.split()[1])
```

 - assumes Country: and Population: occur at start of line
 - assumes Country: before Population:
 - simple cleanups may help, e.g. removing some tags



## HTML DOM

```xml
<HTML>
  <BODY>
    <TABLE>
      <TR>
        <TD>New Zealand:</TD><TD>4,321,321</TD>
        <TD>India:</TD><TD>1,339,000,000</TD>
        ...
      <TR>
    <TABLE>
...
```

Do **not** parse XML or HTML yourself.



## BeautifulSoup parser

 - XML is very uniform:
    `<foo><bar arg="7"><etc/></bar></foo>`
 - HTML is not:
    `<div><img width=70 src="..."><br></dv>`
 - BeautifulSoup is a lenient parser which works out what people
   meant, based on what they wrote.
 - See [BeautifulSoup docs.](http://www.crummy.com/software/BeautifulSoup/bs4/)
   for guide to using BeautifulSoup for scraping.



## lxml

 - A more general purpose [Python XML library](https://lxml.de), with a parser
   equivalent to BeautifulSoup
 - Using / learning lxml will give you a more general purpose
   tool.



## Element recursion

```python
def proc_element(state, element):

```



## XPath


# Data export


# Domain Specific Languages

```
RUN: 201904191310 25 8ef45 200
24 Jan 2018 12:23:34
342 522
542 124
123 452
RUN: 201904191310 25 8ef45 300
24 Jan 2018 12:24:54
423 252
452 241
231 542
```

Data from an Arduino device



## Convert to CSV

```
calib_run,temp_set,unit_id,targconc,time,adc_cond,adc_temp
201904191310,25,8ef45,200,24 Jan 2018 12:23:34,342,522
201904191310,25,8ef45,200,24 Jan 2018 12:23:34,542,124
201904191310,25,8ef45,200,24 Jan 2018 12:23:34,123,452
201904191310,25,8ef45,300,24 Jan 2018 12:24:54,423,252
201904191310,25,8ef45,300,24 Jan 2018 12:24:54,452,241
201904191310,25,8ef45,300,24 Jan 2018 12:24:54,231,542
```



## EBNF grammar

Extended Backus-Naur Form<br/>(e.g. Python syntax docs.)

```
start: block+
block: "RUN:" calib_run temp_set unit_id targconc time obs+

calib_run: NUMBER
temp_set: NUMBER
targconc: NUMBER
unit_id: CHARS
time: DATE
obs: adc_cond adc_temp
adc_cond: NUMBER
adc_temp: NUMBER

%import common.NUMBER
%import common.WS
%ignore WS
S: WS+
CHARS: /\\S+/
DATE: NUMBER S MNTH S NUMBER S CHARS
MNTH: ("Jan"|"Feb"|"Mar"|"Apr"|"May"|"Jun"|"Jul"|"Aug"|"Sep"|"Oct"|"Nov"|"Dec")
"""
```



## Converts anything to a tree of elements

```
  block
    calib_run   201904191310
    temp_set    25
    unit_id     8ef45
    targconc    200
    time        24 Jan 2018 12:23:34
    obs
      adc_cond  342
      adc_temp  522
    obs
      adc_cond  542
      adc_temp  124
    obs
      adc_cond  123
      adc_temp  452
```


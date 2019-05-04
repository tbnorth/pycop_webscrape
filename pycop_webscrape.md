# pycop_webscrape

## pycop_webscrape

https://tbnorth.github.io/pycop_webscrape/

# Overview

 - What is web-scraping
 - Why you shouldn't need to do it
 - Why you shouldn't do it
 - How to do it
   - Getting data
   - Parsing data

# What is web-scraping

Automated collection of data from web pages designed to
be read by people.

# Why you shouldn't need to do it

 - Data rich sites should provide links to download data

AND / OR

 - An API to get data via web requests (REST etc.)

USGS web example - so so example

# Why you shouldn't do it

 - is the data available for sale, is it reasonable to
   bypass that?
 - web access logs will probably be logging your network
   address, is that going to cause concern / misperception?

# Getting content

## urllib

## requests

### Authentication

# Caching content

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

# Parsing content

 - web scraping scripts often specific to a single web site
 - often a static and / or legacy website that won't be changing
 - so the code needn't be perfect, it may only be run once
 - only needs to work for the content that is on the site, no need
   to worry about cases that don't occur
 
## Simple text parsing

```python
result = {}
for line in data['url'][url].split('\n'):
    if "Country" in line:  # Country: New Zealand
        country = line.split(None, 1)[1]
        if "Population" in line:  # Population: 4321321
            result[country] = int(line.split()[1])
```

 - assumes Country: and Population: occur at start of line
 - assumes Country: before Population:
 - simple cleanups may help, e.g.
   `content = content.replace("<p>", "\n")`

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

## BeautifulSoup parser

 - XML is very uniform:
    `<foo><bar arg="7"><etc/></bar></foo>`
 - HTML is not:
    `<div><img width=70 src="..."><br></dv>`
 - BeautifulSoup is a lenient parser which works out what people
   meant, based on what they wrote.

TODO: BeautifulSoup XPath?

## lxml

 - a more general purpose Python XML library, with a parser
   equivalent to BeautifulSoup
 - 
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
RUN: 201904191310 25 8ef45 200
24 Jan 2018 12:23:34
342 522
542 124
123 452
```

Data from an Arduino device

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

%import common.LETTER
%import common.NUMBER
%import common.DIGIT
%import common.WS
%ignore WS
S: WS+
CHARS: /\\S+/
DATE: NUMBER S MNTH S NUMBER S CHARS
MNTH: ("Jan"|"Feb"|"Mar"|"Apr"|"May"|"Jun"|"Jul"|"Aug"|"Sep"|"Oct"|"Nov"|"Dec")
"""

TODO: add log2csv.py example

 - convert anything to a tree of elements
 

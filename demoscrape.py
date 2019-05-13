import json
import os
import requests
from lxml import etree

CACHE_FILE = "scrape.cache.json"

START_URL = "http://www.lakesuperiorstreams.org/streams/allwshed.html"


def get_url(data, url):
    if url not in data['url']:
        print("Fetching '%s'" % url)
        res = requests.get(url)
        data['url'][url] = res.text
    return data['url'][url]


def do_stuff(data):
    # get html str for START_URL
    html = get_url(data, START_URL)
    # get the lenient HTML parser, not the default strict XML parser
    parser = etree.HTMLParser()
    # parse the text into a tree of Element nodes
    tree = etree.XML(html, parser)
    # get the rows using recursion
    rows = recurse_tree(tree)
    for row in rows["__res"][:5]:
        print(row)
    print()

    # get the same list with XPath
    trs = tree.xpath(".//tr[.//a]")
    rows = []
    for tr in trs:
        rows.append([tr.xpath(".//@href")][0])
        tds = tr.xpath("./td")
        rows[-1].extend([' '.join(i.xpath(".//text()")) for i in tds])
    for row in rows[:5]:
        print(row)
    print(set(map(len, rows)))


def recurse_tree(node, state=None):
    if state is None:
        state = {"__res":[]}
    if node.tag == 'thead':
        return
    if node.tag == 'tr':
        state["__res"].append([])

    if node.tag == 'td':
        a = [i for i in node if i.tag == 'a']
        if a:  # anchor / href node
            state["__res"][-1].append(a[0].get('href'))
            state["__res"][-1].append(a[0].text)
        else:
            state["__res"][-1].append(node.text)
    else:
        for child in node:
            ans = recurse_tree(child, state)
    return state


def main():
    if not os.path.exists(CACHE_FILE):
        data = {'url': {}}
    else:
        data = json.load(open(CACHE_FILE))
    try:
        do_stuff(data)
    finally:
        json.dump(data, open(CACHE_FILE, 'w'))


if __name__ == "__main__":
    main()

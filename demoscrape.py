import csv
import json
import os
import requests
import traceback
from lxml import etree

CACHE_FILE = "scrape.cache.json"

START_URL = "http://www.lakesuperiorstreams.org/streams/allwshed.html"

HDRS = "url stream ws_mi2 ws_km2 ws_acres str_mi str_km rds_mi rds_km".split()


def get_url(data, url):
    if url not in data['url']:
        print("Fetching '%s'" % url)
        res = requests.get(url)
        data['url'][url] = res.text
    return data['url'][url]


def norm_space(txt):
    """ '  Some  \n    text  ' -> 'Some text' """
    return ' '.join(txt.split())


def do_stuff(data):
    # get html str for START_URL
    html = get_url(data, START_URL)
    # get the lenient HTML parser, not the default strict XML parser
    parser = etree.HTMLParser()
    # parse the text into a tree of Element nodes
    tree = etree.XML(html, parser)
    # get the rows using recursion
    rows = recurse_tree(tree)

    # show first five rows
    for row in rows["res"][:5]:
        print(row)
    print()

    # get the same list with XPath, get all `tr`s that have an `a` in them
    trs = tree.xpath(".//tr[.//a]")
    rows = []
    for tr in trs:
        # add a new row of output, with the first href in the `tr`
        rows.append([tr.xpath(".//@href")][0])
        # the list of `td` elements in a `tr`
        tds = tr.xpath("./td")
        # get the `text()` from each `td`
        rows[-1].extend([' '.join(i.xpath(".//text()")) for i in tds])
        # clean up whitespace
        rows[-1] = list(map(norm_space, rows[-1]))

    for row in rows[:5]:
        print(row)

    with open("streamdata.csv", 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(HDRS)
        writer.writerows(rows)

    for row in rows:
        get_image(data, START_URL, row)


def recurse_tree(node, state=None):
    if state is None:
        state = {"res": []}
    if node.tag == 'thead':
        return
    if node.tag == 'tr':  # add a new row
        state["res"].append([])

    if node.tag == 'td':
        a = [i for i in node if i.tag == 'a']
        if a:  # anchor / href node
            state["res"][-1].append(a[0].get('href'))
            state["res"][-1].append(a[0].text)
        else:
            state["res"][-1].append(node.text)
    else:
        for child in node:
            recurse_tree(child, state)

    return state


def get_image(data, src_url, row):
    url = row[0]
    url = "{base}/{page}".format(base=os.path.dirname(src_url), page=url)
    html = get_url(data, url)
    parser = etree.HTMLParser()
    tree = etree.XML(html, parser)

    # first try, but they're not all 300 wide after all
    img_src = tree.xpath("//img[@width='300']/@src")
    if not img_src:
        # '..' refers to the parent element
        img_src = tree.xpath("//img[../@align='center']/@src")
        # this doesn't always work either, because of inconsistency
        # note that "if not img_src" let's us use either one
    # turns out this always works
    img_src = tree.xpath("//img[contains(@src, 'images/graphs')]/@src")

    if not img_src:
        print("No image for %s" % (row[1] if len(row) > 1 else "???"))
        return

    if not os.path.exists("imgs"):
        os.mkdir("imgs")
    url = "{base}/{page}".format(base=os.path.dirname(url), page=img_src[0])
    path = os.path.join("imgs", os.path.basename(url))
    if not os.path.exists(path):
        print("Fetching %s" % url)
        res = requests.get(url)
        with open(path, 'wb') as out:
            # .content, not .text, for binary things
            out.write(res.content)


def main():
    if not os.path.exists(CACHE_FILE):
        data = {'url': {}}
    else:
        data = json.load(open(CACHE_FILE))
    try:
        do_stuff(data)
    except Exception:
        traceback.print_exc()
    finally:
        json.dump(data, open(CACHE_FILE, 'w'))


if __name__ == "__main__":
    main()

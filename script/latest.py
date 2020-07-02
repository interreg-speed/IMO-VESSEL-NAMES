#!/usr/bin/env python
import os
import zipfile
from urllib.request import urlopen

from requests_html import HTMLSession

link = "https://www.unece.org/cefact/codesfortrade/codes_index.html"
base = "https://www.unece.org"
session = HTMLSession()

if __name__ == "__main__":
    r = session.get(link)
    all_links = r.html.links
    possible = [link for link in all_links if "mdb.zip" in link]

    li = []

    for link in possible:
        filename = link.split("/")[-1]
        url = urlopen(base + link)
        zipName = 'zipFile.zip'
        output = open(zipName, 'wb')  # note the flag:  "wb"
        output.write(url.read())
        output.close()
        zf = zipfile.ZipFile(zipName)
        zf.extractall("./")
        os.remove(zipName)
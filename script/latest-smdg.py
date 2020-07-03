#!/usr/bin/env python
import csv
import sys

import pandas as pd
import numpy as np
from requests_html import HTMLSession

link = "http://www.smdg.org/smdg-code-lists/"
base = "http://www.smdg.org"
session = HTMLSession()

if __name__ == "__main__":
    r = session.get(link)

    all_links = r.html.links
    possible = [link for link in all_links if "Terminal-Code" in link]

    for link in possible:
        headers="UNLOCODE,Alternative UNLOCODEs,Terminal Code,Terminal Facility Name,Terminal Company Name,Latitude (DMS),Longitude (DMS),Last change,Valid from,Valid until,Terminal Website,Terminal Address,Remarks".split(",")
        df = pd.read_excel(base + link, skiprows=15,encoding=sys.getfilesystemencoding(), names=headers)
        filename=link.split("/")[-1][:-5]
        df.replace(np.nan, '', inplace=True)
        df.replace("\n", '', inplace=True)
        df["Terminal Address"].replace("\n", '', inplace=True, regex=True)
        df["Terminal Company Name"].replace("\n", '', inplace=True,regex=True )
        df.replace(r'\\n',' ', regex=True, inplace=True)
        df.to_csv("data/%s.csv"%filename, index=False,encoding=sys.getfilesystemencoding(), quoting=csv.QUOTE_ALL, quotechar="'")

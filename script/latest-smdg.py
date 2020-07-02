#!/usr/bin/env python
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
        df = pd.read_excel(base + link, skiprows=15)
        filename=link.split("/")[-1][:-5]
        df.replace(np.nan, '', inplace=True)
        df.to_csv("data/%s.csv"%filename, index=False)
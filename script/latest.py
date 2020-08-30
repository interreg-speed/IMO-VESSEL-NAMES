#!/usr/bin/env python3
import os
import sys

import pandas as pd
from chromedriver_py import binary_path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import logging
import pymongo
import ssl
import time

load_dotenv()


class Datasource:
    location_map = {}

    def __init__(self):

        self.service = webdriver.chrome.service.Service(binary_path)
        self.service.start()

        chrome_options = Options()
        chrome_options.add_argument("window-size=1400,600")
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Remote(self.service.service_url, desired_capabilities=chrome_options.to_capabilities())
        self.driver.implicitly_wait(20)
        # self.driver.set_window_size(1920, 1080)

    def do_login(self):
        logging.info("do_login")
        url = "http://www.equasis.org"
        USERNAME = os.environ.get("USERNAME")
        PASSWORD = os.environ.get("PASSWORD")

        self.driver.get(url)
        self.driver.find_element_by_id('home-login').send_keys(USERNAME)
        self.driver.find_element_by_id('home-password').send_keys(PASSWORD)
        self.driver.find_element_by_id('home-password').send_keys(Keys.RETURN)
        return

    def go_home(self):
        self.driver.get("http://www.equasis.org/EquasisWeb/public/HomePage?fs=Search")
        return

    def search_advanced_year(self, start_year="2000",end_year="2001", vessel_type="3"):
        logging.info("grab from start_year %s with end_year %s", start_year, end_year)
        self.driver.find_element_by_id('advancedLink').click()
        # self.driver.find_element_by_id('advanced-search-toggle').click()
        time.sleep(1)
        self.driver.find_element_by_id('P_CatTypeShip_p3').click()
        select = Select(self.driver.find_element_by_id('P_CatTypeShip'))
        select.select_by_value(vessel_type)
        self.driver.find_element_by_id('P_YB_GT').send_keys(start_year)
        self.driver.find_element_by_id('P_YB_LT').send_keys(end_year)
        time.sleep( 1 )
        self.driver.find_element_by_id('buttonAdvSearch').click()
        # self.driver.find_element_by_id('P_YB_GT').send_keys(Keys.RETURN)


    def search_by_name(self, name="MSC"):
        self.driver.find_element_by_name('P_ENTREE_HOME').send_keys(name)
        self.driver.find_element_by_name('P_ENTREE_HOME').send_keys(Keys.RETURN)

    def get_count(self):
        cnt = 0
        try:
            logging.info("get_count")
            text = self.driver.find_element_by_id('ShipId').text
            cnt = text[text.find("(") + 1:-1]
            logging.info("get_count: %s", cnt)
        except Exception as e:
            print(e)

        return cnt

    def has_next(self):
        try:
            self.driver.find_element_by_link_text(">") is not None
        except:
            return False
        return True

    def next_page(self):
        self.driver.find_element_by_link_text(">").click()

    def get_vessels(self):
        vs = []
        try:
            logging.info("get_vessels")

            vessels = self.driver.find_elements_by_css_selector('#ShipResultId tr.hidden-sm')
            vs = []
            logging.info("found %d vessels", len(vessels))
            for item in vessels:
                print(".", end="")
                items = [i.text for i in item.find_elements_by_css_selector('th,td')]
                vs.append(items)
        except Exception as e:
            print(e)
        print(".")
        return vs


class MongoSave:
    db = None
    collection = None
    uri = "mongodb://%s@oceans-shard-00-00.iotwb.mongodb.net:27017,oceans-shard-00-01.iotwb.mongodb.net:27017,oceans-shard-00-02.iotwb.mongodb.net:27017/oceandb?ssl=true&replicaSet=atlas-10a87j-shard-0&authSource=admin&retryWrites=true&w=majority"

    def __init__(self,u_p):
        client = pymongo.MongoClient(self.uri % (u_p), ssl_cert_reqs=ssl.CERT_NONE)
        self.db = client.get_database("oceandb")
        # self.db.create_collection("vessels")
        self.collection = self.db["vessels"]
        print(self.db.list_collection_names())

    def insert(self, vessel_list):
        print("insert - %d" % len(vessel_list))
        arrayed = [{
                    "_id":v[0],
                    "imo":v[0],
                    "name":v[1],
                    "size":v[2],
                    "type":v[3],
                    "built":v[4],
                    "country":v[5]} for v in vessel_list]
        for item in arrayed:
            self.collection.replace_one({"_id":item["_id"]}, item,upsert=True)

def home_and_search(start_year, end_year, vessel_type):
    ds.go_home()
    ds.search_advanced_year(start_year,end_year, vessel_type)
    count = int(ds.get_count())
    return count


if __name__ == "__main__":
    di = sys.argv[1:]
    vessel_type = di[0]
    u_p = os.environ.get("U_P","NONE")

    ds = Datasource()
    # logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    logging.info('Started')
    vessel_types = ["3","4","5"]
    # [1; General Cargo Ships,5; Bulk Carriers, 3; Container Ships, 14; Fishing vessels, 7; Gas Tankers, 10; Offshore Vessels, 6; Oil and Chemical Tankers, 13; Other ships, 8; Other Tankers, 9; Passenger Ships, 4; Ro-Ro Cargo Ships, 11; Service Ships, 2; Specialized Cargo Ships, 12; Tugs]

    ranges = [["1990","2000"],["2000","2005"],["2005","2010"],["2010","2015"],["2015","2020"] ]
    # ranges = [["2005","2010"],["2010","2015"],["2015","2020"] ]

    ds.do_login()
    vessels = []
    ms = MongoSave(u_p)

    for year_range in ranges:
        print("Year range: %s" % year_range)
        try:
            count = home_and_search(start_year=year_range[0], end_year=year_range[1], vessel_type=vessel_type)
        except Exception as e:
            print("E: failed once - %s" % e)
            count = home_and_search(start_year=year_range[0], end_year=year_range[1], vessel_type=vessel_type)

        page = 1
        while True:
            logging.info("starting page %s", page)
            new_vessels = ds.get_vessels()
            ms.insert(new_vessels)
            vessels+=new_vessels
            page += 1
            if ds.has_next():
                ds.next_page()
            else:
                break

    f = pd.DataFrame(vessels, columns="imo,vessel_name,gross_tonnage,type,year_built,flag".split(","))
    f.to_csv("data/%s-vessels.csv" % vessel_type, index=False)
    logging.info('Finished - %s' % vessel_type)


#!/usr/bin/env python
import os

import pandas as pd
from chromedriver_py import binary_path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import logging

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
        self.driver.set_window_size(1920, 1080)

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

    def search_advanced_year(self, year="2000"):
        logging.info("grab from year %s", year)
        self.driver.find_element_by_id('advancedLink').click()
        self.driver.find_element_by_id('P_CatTypeShip_p3').click()
        select = Select(self.driver.find_element_by_id('P_CatTypeShip'))
        select.select_by_value("3")
        self.driver.find_element_by_id('P_YB_GT').send_keys(year)
        self.driver.find_element_by_id('P_YB_GT').send_keys(Keys.RETURN)

    def search_by_name(self, name="MSC"):
        self.driver.find_element_by_name('P_ENTREE_HOME').send_keys(name)
        self.driver.find_element_by_name('P_ENTREE_HOME').send_keys(Keys.RETURN)

    def get_count(self):
        logging.info("get_count")
        text = self.driver.find_element_by_id('ShipId').text
        cnt = text[text.find("(") + 1:-1]
        logging.info("get_count: %s", cnt)
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
        logging.info("get_vessels")

        vessels = self.driver.find_elements_by_css_selector('#ShipResultId tr.hidden-sm')
        vs = []
        logging.info("found %d vessels", len(vessels))
        for item in vessels:
            print(".",end="")
            items = [i.text for i in item.find_elements_by_css_selector('th,td')]
            vs.append(items)
        return vs


if __name__ == "__main__":
    ds = Datasource()
    # logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    logging.info('Started')


    start_year = os.environ.get("START_YEAR","1995")
    ds.do_login()
    vessels = []
    ds.search_advanced_year(start_year)
    count = int(ds.get_count())
    page = 1
    while len(vessels) <= count - 5 and ds.has_next():
        logging.info("starting page %s",page)
        vessels += ds.get_vessels()
        ds.next_page()
        page+=1

    f = pd.DataFrame(vessels, columns="imo,vessel_name,gross_tonnage,type,year_build,flag".split(","))
    f.to_csv("data/container-vessels.csv", index=False)
    logging.info('Finished')


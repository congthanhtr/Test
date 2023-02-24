import time
from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import json


class TourInfomationConfig: 
    tour_info_search_value: str = 'list-group-item'
    tour_property_search_value: str = 'meta-val'
    tour_code_index: int = 0,
    tour_length_index: int = 1,
    tour_from_index: int = 2,
    tour_transport_index: int = 3,
    tour_hotel_rating_index: int = 4,
    tour_start_date_index: int = 5,
    tour_price_index: int = 6, 
    tour_kid_index: int = 7,
    tour_program: str = 'tab-container tabs'
    web_crawl: str = 'https://vietnamtravelmart.com.vn/tour-du-lich/tour-du-lich-trong-nuoc'

    def __init__(self, tour_info_search_value: str,
    tour_property_search_value: str,
    tour_code_index: int,
    tour_length_index: int,
    tour_from_index: int,
    tour_transport_index: int,
    tour_hotel_rating_index: int,
    tour_start_date_index: int,
    tour_price_index: int,
    tour_kid_index: int,
    tour_program: str,
    web_crawl: str):
        self.tour_info_search_value = tour_info_search_value
        self.tour_property_search_value = tour_property_search_value,
        self.tour_code_index = tour_code_index
        self.tour_length_index = tour_length_index
        self.tour_from_index = tour_from_index
        self.tour_transport_index = tour_transport_index
        self.tour_hotel_rating_index = tour_hotel_rating_index
        self.tour_start_date_index = tour_start_date_index
        self.tour_price_index = tour_price_index
        self.tour_kid_index = tour_kid_index
        self.tour_program = tour_program
        self.web_crawl = web_crawl

class TourInformation:
    tour_code: str = None
    tour_length: str = None
    tour_from: str = None
    tour_transport: str = None
    tour_hotel_rate: int = None
    tour_start_date: str = None
    tour_price: str = None
    tour_kid: str = None
    tour_program: str = None 

    @staticmethod
    def load_tour_information(driver: webdriver, config: TourInfomationConfig):
        result = TourInformation()
        list_tour_property = driver.find_elements(By.CLASS_NAME, config.tour_info_search_value)
        if (list_tour_property is not None and len(list_tour_property) > 0):
            result.tour_code = list_tour_property[config.tour_code_index].text.split(':')[1].strip()
            result.tour_length = list_tour_property[config.tour_length_index].text.split(':')[1].strip()
            result.tour_from = list_tour_property[config.tour_from_index].text.split(':')[1].strip()
            result.tour_transport = list_tour_property[config.tour_transport_index].text.split(':')[1].strip()
            result.tour_hotel_rate = len(list_tour_property[config.tour_hotel_rating_index].find_element(By.CLASS_NAME, 'meta-travel-val').find_elements(By.CLASS_NAME, "fa"))
            result.tour_start_date = list_tour_property[config.tour_start_date_index].text.split(':')[1].strip()
            result.tour_price = list_tour_property[config.tour_price_index].text.split(':')[1].strip()
            result.tour_kid = list_tour_property[config.tour_kid_index].text.split(':')[1].strip()
            # process for tour program
            result.tour_program = driver.find_element(By.CLASS_NAME, config.tour_program).get_attribute('innerHTML')
        return result

# init web drvier
driver = webdriver.Edge()
# load config
data = open("crawl_tour/config.json").read()
config = TourInfomationConfig(**json.loads(data))
# go to webpage
driver.get(config.web_crawl)
# get list hot domestic tour
list_hot_tour = list(map(lambda x : x.find_element(By.TAG_NAME, 'a').get_attribute('href'), (driver.find_elements(By.CLASS_NAME, "tour_item"))))
list_tour_info = []
if (list_hot_tour != None and len(list_hot_tour) > 0):
    # go to each tour to crawl
    data = open("crawl_tour/config.json").read()
    config = TourInfomationConfig(**json.loads(data))
    for tour_url in list_hot_tour:
        driver.get(tour_url)
        list_tour_property = driver.find_elements(By.CLASS_NAME, config.tour_info_search_value)
        tour_info = TourInformation.load_tour_information(driver, config)
        list_tour_info.append(tour_info)
        print('pause')

class Crawler:
    driver = webdriver.Edge()

    def load_config():
        data = open("crawl_tour/config.json").read()
        config = TourInfomationConfig(**json.loads(data))
        return config

    def crawl(self, driver: webdriver):
        # init driver
        if (driver is None):
            driver = webdriver.Edge()
        # load config
        config = self.load_config()
        # go to webpage
        driver.get(config.web_crawl)
        # get list hot domestic tour
        list_hot_tour = list(map(lambda x : x.find_element(By.TAG_NAME, 'a').get_attribute('href'), (driver.find_elements(By.CLASS_NAME, "tour_item"))))
        list_tour_info = []
        if (list_hot_tour != None and len(list_hot_tour) > 0):
            # go to each tour to crawl
            data = open("crawl_tour/config.json").read()
            config = TourInfomationConfig(**json.loads(data))
            for tour_url in list_hot_tour:
                driver.get(tour_url)
                list_tour_property = driver.find_elements(By.CLASS_NAME, config.tour_info_search_value)
                tour_info = TourInformation.load_tour_information(driver, config)
                list_tour_info.append(tour_info)
        return list_tour_info
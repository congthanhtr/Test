import re
from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import csv
import time
import json
import pandas as pd

non_char_regex = re.compile("[,\.!?]")


class TourInfomationConfig:
    tour_info_search_value: str = "list-group-item"
    tour_property_search_value: str = "meta-val"
    tour_code_index: int = (0,)
    tour_length_index: int = (1,)
    tour_from_index: int = (2,)
    tour_transport_index: int = (3,)
    tour_hotel_rating_index: int = (4,)
    tour_start_date_index: str = (5,)
    tour_price_index: int = (6,)
    tour_kid_index: str = (7,)
    tour_program: str = "tab-container tabs"
    web_crawl: str = (
        "https://vietnamtravelmart.com.vn/tour-du-lich/tour-du-lich-trong-nuoc"
    )

    def __init__(
        self,
        tour_info_search_value: str,
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
        web_crawl: str,
    ):
        self.tour_info_search_value = tour_info_search_value
        self.tour_property_search_value = (tour_property_search_value,)
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
    tour_name: str = None
    tour_code: str = None
    tour_length: str = None
    tour_from: str = None
    tour_transport: str = None
    tour_hotel_rate: int = None
    tour_start_date: str = None
    tour_price: str = None
    tour_kid: str = None
    tour_program: str = None

    def __init__(
        self,
        tour_name = '',
        tour_code = '',
        tour_length = '',
        tour_from = '',
        tour_transport = '',
        tour_hotel_rate = '',
        tour_start_date = '',
        tour_price = '',
        tour_kid = '',
        tour_program = '',
    ) -> None:
        self.tour_name = tour_name
        self.tour_code = tour_code
        self.tour_length = tour_length
        self.tour_from = tour_from
        self.tour_transport = tour_transport
        self.tour_hotel_rate = tour_hotel_rate
        self.tour_start_date = tour_start_date
        self.tour_price = tour_price
        self.tour_kid = tour_kid
        self.tour_program = tour_program

    @staticmethod
    def load_tour_information(driver: webdriver, config: TourInfomationConfig):
        result = TourInformation()
        list_tour_property = driver.find_elements(
            By.CLASS_NAME, config.tour_info_search_value
        )
        if list_tour_property is not None and len(list_tour_property) > 0:
            result.tour_name = driver.title.split("-")[0].strip()
            result.tour_code = (
                list_tour_property[config.tour_code_index].text.split(":")[1].strip()
            )
            result.tour_length = (
                list_tour_property[config.tour_length_index].text.split(":")[1].strip()
            )
            result.tour_from = (
                list_tour_property[config.tour_from_index].text.split(":")[1].strip()
            )
            result.tour_transport = (
                list_tour_property[config.tour_transport_index]
                .text.split(":")[1]
                .strip()
            )
            result.tour_start_date = (
                list_tour_property[config.tour_start_date_index]
                .text.split(":")[1]
                .strip()
            )

            # process for price
            currency = ["VNĐ", "USD", "đ", "$", "."]
            result.tour_price = (
                list_tour_property[config.tour_price_index].text.split(":")[1].strip()
            )
            result.tour_kid = (
                list_tour_property[config.tour_kid_index].text.split(":")[1].strip()
            )
            for c in currency:
                if c in result.tour_price:
                    result.tour_price = result.tour_price.replace(c, "").strip()
                if c in result.tour_kid:
                    result.tour_kid = result.tour_kid.replace(c, "").strip()

            # process for number of hotel rate
            result.tour_hotel_rate = len(
                list_tour_property[config.tour_hotel_rating_index]
                .find_element(By.CLASS_NAME, "meta-travel-val")
                .find_elements(By.CLASS_NAME, "fa")
            )
            # process for tour program
            result.tour_program = driver.find_element(
                By.CLASS_NAME, config.tour_program
            ).get_attribute("innerHTML")
        return result


class Crawler:
    driver: webdriver = None

    def load_config(self):
        data = open("static/config.json").read()
        config = TourInfomationConfig(**json.loads(data))
        return config

    def crawl(self, driver: webdriver):
        # init driver
        if self.driver is None:
            self.driver = webdriver.Edge()
        else:
            self.driver = driver
        # load config
        config = self.load_config()
        # go to webpage
        self.driver.get(config.web_crawl)
        # get list hot domestic tour
        list_hot_tour = list(
            map(
                lambda x: x.find_element(By.TAG_NAME, "a").get_attribute("href"),
                (self.driver.find_elements(By.CLASS_NAME, "tour_item")),
            )
        )
        list_tour_info: list[TourInformation] = []
        if list_hot_tour is not None and len(list_hot_tour) > 0:
            # go to each tour to crawl
            for tour_url in list_hot_tour:
                self.driver.get(tour_url)
                tour_info = TourInformation.load_tour_information(self.driver, config)
                list_tour_info.append(tour_info)
        list_tour_info_to_csv = [
            [
                tour.tour_name,
                tour.tour_code,
                tour.tour_length,
                tour.tour_from,
                tour.tour_transport,
                tour.tour_hotel_rate,
                tour.tour_start_date,
                tour.tour_price,
                tour.tour_kid,
                tour.tour_program
            ]
            for tour in list_tour_info
        ]
        df = pd.DataFrame(list_tour_info_to_csv)
        df.to_csv(
            "static/crawl.csv",
            index=False,
            header=[
                "TourName",
                "TourCode",
                "TourLength",
                "TourFrom",
                "TourTransport",
                "TourHotelRate",
                "TourStartDate",
                "TourPrice",
                "TourKid",
                "TourProgram"
            ],
        )
        return list_tour_info

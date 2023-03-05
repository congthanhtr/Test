import re
from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import csv
import json
from .myutils import util

from .model.tour_information import (
    TourInfomation,
    TourProgramDetail,
    TourProgramDetail_InADay,
    ConfigTourLengthType,
    ConfigTourTransport,
)

non_char_regex = re.compile("[,\.!?]")
class Crawler:
    driver: ChromiumDriver = None 

    def load_config(self):
        config = json.load(open('static/config.json'))
        return config

    config: dict = None
    
    def __init__(self) -> None:
        if self.driver is None:
            self.driver = webdriver.Edge()

        if self.config is None:
            self.config = self.load_config()
            
    def crawl_link_tour(self):
        """
        Crawl link của các tour hot trên trang
        """
        # open website to crawl:
        self.driver.get(self.config['source_web'])
        # get list link of tour using
        list_tour = list(map(lambda tour: tour.find_element(By.TAG_NAME, 'a').get_attribute('href'), self.driver.find_element(By.CLASS_NAME, self.config['class_value_list_tour']).find_elements(By.TAG_NAME, 'li')))
        if list_tour is not None and len(list_tour) > 0:
            with open('static/links.txt', 'w') as f:
                f.write('\n'.join(list_tour))
                f.close()

    def crawl_tour_detail(self):
        """
        Crawl toàn bộ thông tin của tất cả các tour
            Trả về:
                List các tour với thông tin cần thiết
        """
        list_tour_info: list[TourInfomation] = []
        list_link_tour = open('static/links.txt').read().splitlines()
        if list_link_tour is not None and len(list_link_tour) > 0:
            for link_tour in list_link_tour:
                self.driver.get(link_tour)
                print(link_tour)
                tour = self.crawl_tour_general_info(TourInfomation())
                list_tour_info.append(tour)
        else:
            raise Exception('List load from file is None or Empty')
        return list_tour_info
    
    def crawl_tour_general_info(self, tour: TourInfomation):
        """
        Hàm con của crawl_tour_detail
            Trả về: TourInformation
                Thông tin của 1 tour: địa điểm bắt đầu, độ dài tour, phương tiện di chuyển và phương trình tour
        """
        tour_general_info_region = self.driver.find_element(By.CLASS_NAME, self.config['class_value_info_tour']).find_element(By.TAG_NAME, 'tr')
        tour_general_infos = tour_general_info_region.find_elements(By.TAG_NAME, 'td')
        tour.start_from = self.tour_general_info_start_from(tour_general_infos[0])
        tour.length = self.tour_general_info_tour_length(tour_general_infos[1])
        tour.transport = self.tour_general_info_tour_transport(tour_general_infos[2])
        tour.tour_program = self.tour_general_info_tour_program()
        return tour
    
    def tour_general_info_start_from(self, element: WebElement):
        """
        Hàm con của crawl_tour_general_info:
            Trả về:
                string: địa điểm khởi hành tour
        """
        return element.text
    
    def tour_general_info_tour_length(self, element: WebElement):
        """
        Hàm con của crawl_tour_general_info:
            Trả về:
                tuple: (số ngày, số đêm)
        """
        tour_length = element.text
        return TourInfomation.to_length(tour_length)


    def tour_general_info_tour_transport(self, element: WebElement):
        """
        Hàm con của crawl_tour_general_info:
            Trả về:
                list[string]: list các phương tiện có sử dụng trong tour
        """
        list_img = element.find_elements(By.TAG_NAME, 'img')
        list_transport: list[str] = []
        if (list_img is not None and len(list_img) > 0):
            for img in list_img:
                title = img.get_attribute('title')
                list_transport.append(title)
        return list_transport
    
    def tour_general_info_tour_program(self):
        """
        Hàm con của crawl_tour_general_info:
            Trả về:
                str: Chương trình tour chi tiết 
        """
        return ""



import re
from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import csv
import json
from .myutils import util

from .tour_information import (
    TourInfomation,
    TourProgramDetail,
    TourProgramDetail_InADay,
    ConfigTourLengthType,
    ConfigTourTransport,
)

non_char_regex = re.compile("[,\.!?]")


class Crawler:
    driver: ChromiumDriver = None
    config: dict = None

    def load_config(self):
        config = json.load(open("static/config.json"))
        return config

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
        self.driver.get(self.config["source_web"])
        # get list link of tour using
        list_tour = list(
            map(
                lambda tour: tour.find_element(By.TAG_NAME, "a").get_attribute("href"),
                self.driver.find_element(
                    By.CLASS_NAME, self.config["class_value_list_tour"]
                ).find_elements(By.TAG_NAME, "li"),
            )
        )
        if list_tour is not None and len(list_tour) > 0:
            with open("static/links.txt", encoding="utf-8", mode="w") as f:
                f.write("\n".join(list_tour))
                f.close()

    def crawl_tour_detail(self):
        """
        Crawl toàn bộ thông tin của tất cả các tour
            Trả về:
                List các tour với thông tin cần thiết
        """
        list_tour_info: list[TourInfomation] = []
        list_link_tour = open("static/links.txt").read().splitlines()
        if list_link_tour is not None and len(list_link_tour) > 0:
            for link_tour in list_link_tour:
                tour = TourInfomation()
                self.driver.get(link_tour)
                self.try_open_read_more()
                tour = self.crawl_tour_general_info(tour)
                list_tour_info.append(tour)
            # with open("static/data.csv", encoding="utf-8", mode="w") as f:
            #     write = csv.writer(f)
            #     for tour in list_tour_info:
            #         write.writerow(
            #             [tour.start_from, tour.length, tour.transport, tour.program]
            #         )
        else:
            raise Exception("List load from file is None or Empty")
        return list_tour_info

    def crawl_tour_general_info(self, tour: TourInfomation):
        """
        Hàm con của crawl_tour_detail
            Trả về: TourInformation
                Thông tin của 1 tour: địa điểm bắt đầu, độ dài tour, phương tiện di chuyển và phương trình tour
        """
        tour_general_info_region = self.driver.find_element(
            By.CLASS_NAME, self.config["class_value_info_tour"]
        ).find_element(By.TAG_NAME, "tr")
        tour_general_infos = tour_general_info_region.find_elements(By.TAG_NAME, "td")
        tour.name = self.driver.find_element(
            By.CLASS_NAME, self.config["class_value_tour_name"]
        ).text
        tour.start_from = self.tour_general_info_start_from(tour_general_infos[0])
        tour.length = self.tour_general_info_tour_length(
            tour_general_infos[1], tour.name
        )
        tour.transport = self.tour_general_info_tour_transport(tour_general_infos[2])
        tour.price = self.tour_general_info_tour_price(
            self.driver.find_element(
                By.CLASS_NAME, self.config["class_value_tour_price"]
            )
        )
        tour.program = self.tour_general_info_program(tour)
        return tour

    def tour_general_info_start_from(self, element: WebElement):
        """
        Hàm con của crawl_tour_general_info:
            Trả về:
                string: địa điểm khởi hành tour
        """
        return element.text

    def tour_general_info_tour_length(self, element: WebElement, tour_name: str):
        """
        Hàm con của crawl_tour_general_info:
            Trả về:
                tuple: (số ngày, số đêm)
        """
        tour_length = element.text
        return TourInfomation.to_length(tour_length, tour_name)

    def tour_general_info_tour_transport(self, element: WebElement):
        """
        Hàm con của crawl_tour_general_info:
            Trả về:
                list[string]: list các phương tiện có sử dụng trong tour
        """
        list_img = element.find_elements(By.TAG_NAME, "img")
        list_transport: list[str] = []
        if list_img is not None and len(list_img) > 0:
            for img in list_img:
                title = img.get_attribute("title")
                list_transport.append(title)
        return list_transport

    def tour_general_info_tour_price(self, element: WebElement):
        return TourInfomation.to_price(element.text)

    def tour_general_info_program(self, tour: TourInfomation):
        """
        Hàm con của crawl_tour_general_info:
            Trả về:
                TourInformation: Chương trình tour chi tiết
        """
        if tour.length[0] == 1 and tour.length == 0:  # nếu là tour 1 ngày
            asd = self.crawl_tour_one_day()
        else:  # nếu là tour nhiều ngày
            asd = self.crawl_tour_many_days(
                tour,
                self.driver.find_element(By.ID, self.config["id_value_tab_program"]),
            )
        return asd

    def crawl_tour_one_day(self):
        pass

    def crawl_tour_many_days(self, tour: TourInfomation, parent_element: WebElement):
        """
        Crawl các thông tin cho tour đi nhiều ngày
        """
        list_days_in_tour: list[TourProgramDetail_InADay] = []
        if parent_element is not None:
            day_header = parent_element.find_elements(
                By.TAG_NAME, "h3"
            )  # lấy danh sách các ngày trong chương trình tour được gạch chân
            num_of_day = tour.length[0] + 1 if tour.length[0] == tour.length[1] else tour.length[0]
            for i in range(0, num_of_day):
                detail = TourProgramDetail_InADay()
                # tóm tắt tour trong ngày
                day_i_header_text = day_header[
                    i
                ].text  # text ngày thứ i trong chương trình tour
                detail.summary = day_i_header_text
                # no of day
                no_of_day = i + 1
                detail.no_of_day = no_of_day
                # thông tin bữa ăn
                is_contains_day, day_text = util.contains_day(
                    day_i_header_text, no_of_day
                )
                if is_contains_day:
                    meals = day_i_header_text.split("(")[1].lower()
                    detail = detail.crawl_meals_info(meals)
                # gala dinner
                detail = detail.crawl_gala_dinner(tour_name=tour.name)
                # hướng dẫn viên
                detail = detail.crawl_tour_guide(
                    self.driver.find_element(
                        By.CLASS_NAME, self.config["class_value_extra_services"]
                    ).text.split("  ")
                )
                # đi lại
                detail = detail.crawl_transport_info(transports=tour.transport)
                # chương trình tour
                #   lấy tour program dưới dạng text
                tour_program_text: str = ''
                if i < num_of_day - 1:
                    middle = util.find_between_element(day_header[i], day_header[i+1])
                else:
                    middle = util.find_between_element(day_header[i], None)
                
                detail = detail.crawl_program_tour([elem.text.strip() for elem in middle])
                # điểm đến
                list_destination: list[str] = day_i_header_text.split('(')[0].lower().replace(day_text + ' |', '').split('-')
                list_destination_stripped = [des.strip() for des in list_destination]
                detail = detail.crawl_destination(list_destination=list_destination_stripped)
                # cảnh báo

                # dịch vụ (khách sạn, nhà nghỉ)

                list_days_in_tour.append(detail)
        return list_days_in_tour


    def crawl_meals_info(self, meals: str, detail: TourProgramDetail_InADay):
        """
        Hàm chức năng của crawl_tour_many_days:
            Crawl các thông tin liên quan đến bữa ăn
        """
        if util.is_contains(meals, TourProgramDetail.THREEMEALS):
            detail.has_breakfast = True
            detail.has_lunch = True
            detail.has_dinner = True
            return detail
        if meals.__contains__(TourProgramDetail.TWOMEALS):
            detail.has_breakfast = True
            detail.has_dinner = True
            return detail
        if meals.__contains__(TourProgramDetail.MORNING):
            detail.has_breakfast = True
        if meals.__contains__(TourProgramDetail.NOON):
            detail.has_lunch = True
        if meals.__contains__(TourProgramDetail.EVENNING):
            detail.has_dinner = True
        return detail

    def crawl_transport_info(
        self, tour: TourInfomation, detail: TourProgramDetail_InADay
    ):
        """
        Hàm chức năng của crawl_tour_many_days:
            Crawl các thông tin liên quan đến phương tiện di chuyển
        """
        transports = tour.transport
        if ConfigTourTransport.COACH in transports:
            detail.use_coach = True
        if ConfigTourTransport.AIRPLANE in transports:
            detail.use_air_plane = True
        if ConfigTourTransport.SHIP in transports:
            detail.use_ship = True
        if ConfigTourTransport.TRAIN in transports:
            detail.use_train = True
        return detail

    def crawl_program_tour(self, tour_program: str):
        """
        Hàm chức năng của crawl_tour_many_days:
           Crawl các thông tin liên quan đến chương trình tour
        """
        pass
    
    def try_open_read_more(self):
        try:
            self.driver.find_element(By.ID, self.config['id_value_tab_program']).find_element(By.CLASS_NAME, self.config['class_value_read_more']).find_element(By.TAG_NAME, 'span').click()
        except:
            pass

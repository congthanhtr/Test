from selenium.webdriver.support import expected_conditions as EC

from .myutils import util


class ConfigTourLengthType:
    ADAY = 1
    MULTIPLEDAYANDNIGHT = 2

    tour_length_type_mapping = {
        "1 ngày": ADAY,
        "1 ngày 1 đêm": ADAY,
        "một ngày": ADAY,
        "một ngày một đêm": ADAY,
    }

    def get_tour_length_type(self, tour_length: str):
        if tour_length.lower() in self.tour_length_type_mapping:
            return self.tour_length_type_mapping[tour_length]
        else:
            return self.MULTIPLEDAYANDNIGHT


class ConfigTourTransport:
    COACH: str = "Xe"
    AIRPLANE: str = "Máy bay"
    SHIP: str = "Tàu thủy"
    TRAIN: str = "Tàu hỏa"


class TourProgramDetailConst:
    # const
    MORNING: str = "sáng"
    NOON: str = "trưa"
    AFTERNOON: str = "chiều"
    EVENNING: str = "tối"
    GALA: str = "gala"
    THREEMEALS = "3 bữa"
    TWOMEALS = "2 bữa"
    TOUR_GUIDE = "hướng dẫn viên"
    HOTEL = "khách sạn"
    RESTAURANT = "nhà hàng"


class TourProgramDetail(TourProgramDetailConst):
    """
    Chi tiết chương trình tour trong 1 ngày
    """

    # ăn uống
    has_breakfast: bool = False
    has_lunch: bool = False
    has_dinner: bool = False
    has_gala_dinner: bool
    # vé
    need_ticket: bool = False
    need_visa: bool = False
    # dịch vụ
    use_hotel: bool = False
    use_restaurant: bool = False
    use_cruise: bool = False
    has_tour_guide: bool = False
    # đi lại
    use_coach: bool = False
    use_air_plane: bool = False
    use_ship: bool = False
    use_train: bool = False
    # điểm đến
    destination: list[str] = []
    # cảnh báo
    is_good_weather: bool = False


class TourProgramDetail_Crawler:
    def crawl_meals_info(self, meals: str):
        """
        Hàm chức năng của crawl_tour_many_days:
            Crawl các thông tin liên quan đến bữa ăn
        """
        pass

    def crawl_transport_info(self, transports: list[str]):
        """
        Hàm chức năng của crawl_tour_many_days:
            Crawl các thông tin liên quan đến phương tiện di chuyển
        """
        pass

    def crawl_program_tour(self, tour_program: str):
        """
        Hàm chức năng của crawl_tour_many_days:
           Crawl các thông tin liên quan đến chương trình tour
        """
        pass

    def crawl_gala_dinner(self, tour_name: str):
        """
        Crawl thông tin liên quan đến gala dinner
        """
        pass

    def crawl_tour_guide(self, extra_services: list[str]):
        pass

    def crawl_destination(self, list_destination: list[str]):
        """
        Crawl các thông tin liên quan đến địa điểm đến trong ngày
        """
        pass

    def crawl_hotel_service(self):
        """
        Crawl các thông tin liên quan đến việc sử dụng dịch vụ nhà hàng/khách sạn
        """
        pass


class TourProgramDetail_InADay(TourProgramDetail, TourProgramDetail_Crawler):
    """
    Chi tiết chương trình tour dài 1 ngày
    """

    summary: str = ""
    no_of_day: int = 0
    morning: str = ""
    noon: str = ""
    afternoon: str = ""
    evenning: str = ""

    def crawl_meals_info(self, meals: str):
        if util.is_contains(meals, TourProgramDetail.THREEMEALS):
            self.has_breakfast = True
            self.has_lunch = True
            self.has_dinner = True
            return self
        if util.is_contains(meals, TourProgramDetail.TWOMEALS):
            self.has_breakfast = True
            self.has_dinner = True
            return self
        if util.is_contains(meals, TourProgramDetail.MORNING):
            self.has_breakfast = True
        if util.is_contains(meals, TourProgramDetail.NOON):
            self.has_lunch = True
        if util.is_contains(meals, TourProgramDetail.EVENNING):
            self.has_dinner = True
        return self

    def crawl_transport_info(self, transports: list[str]):
        """
        Hàm chức năng của crawl_tour_many_days:
            Crawl các thông tin liên quan đến phương tiện di chuyển
        """
        if ConfigTourTransport.COACH in transports:
            self.use_coach = True
        if ConfigTourTransport.AIRPLANE in transports:
            self.use_air_plane = True
        if ConfigTourTransport.SHIP in transports:
            self.use_ship = True
        if ConfigTourTransport.TRAIN in transports:
            self.use_train = True
        return self

    def crawl_gala_dinner(self, tour_name: str):
        if util.is_contains(tour_name, TourProgramDetail.GALA):
            self.has_gala_dinner = True
        return self

    def crawl_tour_guide(self, extra_services: list[str]):
        if TourProgramDetail.TOUR_GUIDE in extra_services:
            self.has_tour_guide = True
        return self

    def crawl_program_tour(self, tour_program: list[str]):
        for i in range(0, len(tour_program)):
            # sử dụng dịch vụ nhà hàng khách sạn
            if util.is_contains(tour_program[i], TourProgramDetail.HOTEL):
                self.use_hotel = True
            if util.is_contains(tour_program[i], TourProgramDetail.RESTAURANT):
                self.use_restaurant = True
            # crawl chương trình tour
            # self.morning = 'morning'
            self.noon = 'noon'
            self.afternoon = 'afternoon'
            self.evenning = 'evening'
            # morning_process =  self.process_tour_program_foreach(
            #     tour_program=tour_program,
            #     start_index=i,
            #     time=self.morning,
            #     time_text=self.MORNING,
            #     not_include_time_text=[self.NOON, self.AFTERNOON, self.EVENNING],
            # )
            # if (not util.is_null_or_empty(morning_process)):
            #     print(morning_process)
            #     self.morning = morning_process
        return self

    def crawl_destination(self, list_destination: list[str]):
        self.destination = []
        for destination in list_destination:
            city = util.find_city_for_destination(destination=destination)
            if city not in self.destination:
                self.destination.append(city)
        return self

    def process_tour_program(self, tour_program: list[str], start_index: int):
        morning_process =  self.process_tour_program_foreach(
            tour_program=tour_program,
            start_index=start_index,
            time=self.morning,
            time_text=self.MORNING,
            not_include_time_text=[self.NOON, self.AFTERNOON, self.EVENNING],
        )
        if not util.is_null_or_empty(morning_process):
            self.morning = morning_process
        else:
            self.morning = self.morning
        # self.process_tour_program_foreach(
        #     tour_program=tour_program,
        #     start_index=start_index,
        #     time=self.noon,
        #     time_text=self.NOON,
        #     not_include_time_text=[self.MORNING, self.AFTERNOON, self.EVENNING],
        # )
        # self.process_tour_program_foreach(
        #     tour_program=tour_program,
        #     start_index=start_index,
        #     time=self.afternoon,
        #     time_text=self.AFTERNOON,
        #     not_include_time_text=[self.NOON, self.MORNING, self.EVENNING],
        # )
        # self.process_tour_program_foreach(
        #     tour_program=tour_program,
        #     start_index=start_index,
        #     time=self.evenning,
        #     time_text=self.EVENNING,
        #     not_include_time_text=[self.NOON, self.AFTERNOON, self.MORNING],
        # )

    def process_tour_program_foreach(
        self,
        tour_program: list[str],
        start_index: int,
        time: str,
        time_text: str,
        not_include_time_text: list[str],   
    ):
        temp_str: str = ''
        for i in range(start_index, len(tour_program)):
            at_time = tour_program[i].split(":")[0]
            if util.is_equals(at_time, time_text):
                temp_str = tour_program[i]
                for j in range(i + 1, len(tour_program)):
                    at_time = tour_program[j].split(":")[0]
                    if at_time not in not_include_time_text:
                        temp_str += tour_program[j]
        return temp_str


class TourInfomation:
    name: str = ""
    start_from: str = ""
    length: tuple = ()
    transport: list[str] = []
    price: int = 0
    num_of_destinations: int = 0
    program: list[TourProgramDetail_InADay] = []
    weather: bool = False

    DAY = "ngày"
    NIGHT = "đêm"
    NIGHT_INSHORT = "1n1d"
    NIGHT_INSHORT1 = "1n1đ"
    NIGHT_INFULL = "1 ngày 1 đêm"
    NIGHT_INFULL_TEXT = "một ngày một đêm"
    DEFAULT_NIGHT_ZERO = 0  # tour 1 ngày 0 đêm
    DEFAULT_NIGHT_ONE = 1  # tour 1 ngày 1 đêm
    VND = "VND"
    VNDPERONE = "VND/người"

    @staticmethod
    def to_length(tour_length: str, tour_name: str):
        tour_length = tour_length.lower()
        inday = True if not tour_length.__contains__(TourInfomation.NIGHT) else False
        tour_length = tour_length.replace(TourInfomation.DAY, "")
        tour_length = tour_length.replace(TourInfomation.NIGHT, "")
        if not inday:
            return (int(tour_length[0]), int(tour_length[3]))
        else:
            return (
                int(tour_length[0]),
                TourInfomation.DEFAULT_NIGHT_ZERO
                if (
                    not util.is_contains(tour_name, TourInfomation.NIGHT_INSHORT)
                    and not util.is_contains(tour_name, TourInfomation.NIGHT_INSHORT1)
                    and not util.is_contains(tour_name, TourInfomation.NIGHT_INFULL)
                    and not util.is_contains(
                        tour_name, TourInfomation.NIGHT_INFULL_TEXT
                    )
                )
                else TourInfomation.DEFAULT_NIGHT_ONE,
            )

    @staticmethod
    def to_price(price: str):
        true_price = price.split("\n")[1] if len(price.split("\n")) > 1 else price
        true_price = true_price.replace(TourInfomation.VNDPERONE, "").strip()
        true_price = true_price.replace(TourInfomation.VND, "").strip()
        true_price = true_price.replace(",", "").strip()
        return int(true_price)

    def is_one_day(self):
        if self.length[0] > 0:
            return True
        return False

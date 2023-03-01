import json
from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

class ConfigTourLengthType:
    ADAY = 1
    MULTIPLEDAYANDNIGHT = 2

    tour_length_type_mapping = {
        '1 ngày': ADAY,
        '1 ngày 1 đêm': ADAY,
        'một ngày': ADAY,
        'một ngày một đêm': ADAY
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
        
class TourProgramDetail:
    """
    Chi tiết chương trình tour trong 1 ngày
    """

    # ăn uống
    has_breakfast: bool
    has_lunch: bool
    has_dinner: bool
    has_gala_dinner: bool
    # vé
    need_ticket: bool
    need_visa: bool
    # dịch vụ
    use_hotel: bool
    use_restaurant: bool
    use_cruise: bool
    has_tour_guide: bool
    # đi lại
    use_coach: bool
    use_air_plane: bool
    use_ship: bool
    use_train: bool
    # điểm đến
    destination: list[str]
    # cảnh báo
    is_good_weather: bool


class TourProgramDetail_InADay(TourProgramDetail):
    """
    Chi tiết chương trình tour dài 1 ngày
    """
    NoOfDay: int
    Morning: str
    Noon: str
    Afternoon: str
    Evenning : str

    MORNING: str = "Sáng"
    NOON: str = "Trưa"
    AFTERNOON: str = "Chiều"
    EVENNING: str = "Tối"
    

class TourInfomation:
    start_from: str
    length: tuple
    transport: list[str]
    tour_program: list[TourProgramDetail_InADay]

    DAY = 'ngày'
    NIGHT = 'đêm'
    DEFAULT_NIGHT = 0


    @staticmethod
    def to_length(tour_length: str):
        tour_length = tour_length.lower()
        inday = True if not tour_length.__contains__(TourInfomation.NIGHT) else False
        tour_length = tour_length.replace(TourInfomation.DAY, '')
        tour_length = tour_length.replace(TourInfomation.NIGHT, '')
        if inday:
            return (tour_length[0], tour_length[3])
        else:
            return (tour_length[0], TourInfomation.DEFAULT_NIGHT)

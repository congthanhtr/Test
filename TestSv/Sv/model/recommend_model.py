from .hotel_model import HotelModel


class TourProgramModel:
    hotel: HotelModel
    no_of_day: int = 0
    province = None
    pois: list = []

    def __init__(self) -> None:
        self.hotel = None
        self.no_of_day = 0
        self.province = None
        self.pois = []

class RecommendModel:
    num_of_day: int = 0
    num_of_night: int = 0
    cities_from: list = []
    cities_to: list = []
    type_of_tour: int = 0
    cost_range: float = 0.0
    main_transport: str = ''
    program: list[TourProgramModel, dict] = []
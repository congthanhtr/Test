class TourProgramModel:
    no_of_day: int = 0
    province = None
    pois: list = []


class RecommendModel:
    num_of_day: int = 0
    num_of_night: int = 0
    cities_from: list = []
    cities_to: list = []
    type_of_tour: int = 0
    cost_range: float = 0.0
    program: list[TourProgramModel] = []
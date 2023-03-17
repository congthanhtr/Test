from ..ml_model.ml_service import MachineLearningService
from .time_travel import TimeTravelService
from ..myutils import util

import pandas as pd


class RecommendModel:
    num_of_day: int = 0
    num_of_night: int = 0
    cities_from: list = []
    cities_to: list = []
    type_of_tour: int = 0
    cost_range: float = 0.0


class RecommendService:
    num_of_day: int = 0
    num_of_night: int = 0
    cities_from: list = []
    cities_to: list = []
    type_of_tour: int = 0
    cost_range: float = 0.0

    ml_service = MachineLearningService()
    time_travel_service = TimeTravelService()

    def __init__(
        self,
        num_of_day: int,
        num_of_night: int,
        cities_from: list,
        cities_to: list,
        type_of_tour: int,
        cost_range: float,
    ) -> None:
        self.num_of_day = num_of_day
        self.num_of_night = num_of_night

        # transform city code to string
        self.cities_from = []
        for cf in cities_from:
            self.cities_from.append(util.get_province_name_by_code(cf))

        self.cities_to = []
        for ct in cities_to:
            self.cities_to.append(util.get_province_name_by_code(ct))

        self.type_of_tour = type_of_tour
        self.cost_range = cost_range

    def recommend(self):
        # predict vihicles
        list_travel_time_by_each_vihicle = [] # bao gồm xe ô tô
        travel_by_plane, flight_time, driving_time = self.should_travel_by_plane(self.cities_from, self.cities_to)
        list_travel_time_by_each_vihicle.extend([flight_time, driving_time])
        for travel_time in list_travel_time_by_each_vihicle:
            if travel_time == 0:
                continue
            

        # predict places

        return self

    def should_travel_by_plane(self, cities_from, cities_to) -> tuple:
        predict_vihicles = self.ml_service.get_predict_vihicles_model()
        time_travel_model = self.time_travel_service.calculate_time_travel(
            cities_from, cities_to
        )
        predict_data = [
            time_travel_model.distance,
            time_travel_model.flight_time,
            time_travel_model.driving_time,
            self.num_of_day,
            self.num_of_night,
            self.type_of_tour,
        ]
        df = pd.DataFrame([predict_data])

        return (True, time_travel_model.flight_time, time_travel_model.driving_time) if predict_vihicles.model.predict(df) == ['Yes'] else (False, time_travel_model.flight_time, time_travel_model.driving_time)
        

from ..ml_model.ml_service import MachineLearningService
from .time_travel import TimeTravelService
from ..myutils import util

import pandas as pd

from ..model.recommend_model import RecommendModel, TourProgramModel

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
        # init result
        recommend_model = RecommendModel()
        recommend_model.num_of_day = self.num_of_day
        recommend_model.num_of_night = self.num_of_night
        recommend_model.cities_from = self.cities_from
        recommend_model.cities_to = self.cities_to
        recommend_model.type_of_tour = self.type_of_tour
        recommend_model.cost_range = self.cost_range
        recommend_model.program = []
        
        # validate input
        # validate input model goes here

        # get distance matrix from cities_from
        province_distance_matrix = self.to_distance_matrix(self.cities_to)
        #region reorder the list city to go
        mstree = self.get_minium_spanning_tree(province_distance_matrix) # now have the order to go
        temp = []
        for i in range(0, len(mstree)):
            temp.append(self.cities_to[mstree[i]])
        self.cities_to = temp
        #endregion
        # predict vihicles
        list_travel_time_by_each_vihicle = [] # contains time to go by each vihicle (plane, car,...)
        travel_by_plane, flight_time, driving_time = self.should_travel_by_plane(self.cities_from, self.cities_to)
        list_travel_time_by_each_vihicle.extend([flight_time, driving_time])
        
        # divide equally time to each province
        list_travel_time_by_each_province = util.divide_equally(self.num_of_day, len(self.cities_to))

        # build program tour
        for travel_time in list_travel_time_by_each_vihicle:
            if travel_time == 0:
                continue

            no_of_day = 1 # day no.1 2 3...
            # get list travel time (like travel time from A to B (minutes), B to C,...)
            list_travel_time_between_provinces = [] 
            list_travel_time_between_provinces.append(travel_time)
            if len(self.cities_to) > 1:
                for i in range(1, len(self.cities_to)):
                    city_a_cord = util.get_lat_lon([self.cities_to[i-1]])[0]
                    city_b_cord = util.get_lat_lon([self.cities_to[i]])[0]
                    dist = util.get_distance_between_two_cord(city_a_cord, city_b_cord)
                    driv_time = self.time_travel_service._calculate_driving_time(dist)
                    list_travel_time_between_provinces.append(driv_time)
            for i in range(0, len(self.cities_to)):
                is_last_province = 1 if i == (len(self.cities_to) - 1) else 0
                driving_time_between_province = list_travel_time_between_provinces[i] if not is_last_province else list_travel_time_between_provinces[i] + travel_time
                # get num of places that we will visit in each province
                n_places = round(self.get_n_places(list_travel_time_by_each_province[i], driving_time_between_province, self.cost_range, len(self.cities_to), is_last_province)[0]) 
                # ex: 5
                n_places_each_day = util.divide_equally(n_places, list_travel_time_by_each_province[i]) # num of places that we will visit each day in that province
                # ex: [3, 2]
                for j in range(0, len(n_places_each_day)):
                    tour_program = TourProgramModel()
                    tour_program.province = self.cities_to[i]
                    tour_program.no_of_day = no_of_day
                    # request to get n_places_each_day[i] places
                    tour_program.pois = ['1' for k in range(0, n_places_each_day[j])]
                    no_of_day = no_of_day + 1
                    recommend_model.program.append(tour_program)
                
        # predict places

        return recommend_model

    def should_travel_by_plane(self, cities_from, cities_to) -> tuple:
        predict_vihicles = self.ml_service.get_predict_vihicles_model()
        time_travel_model = self.time_travel_service.calculate_time_travel(
            cities_from, cities_to
        )
        predict_data = [
            time_travel_model.distance, # distance
            time_travel_model.flight_time, # flight time
            time_travel_model.driving_time, # driving time
            self.num_of_day, # num of day
            self.num_of_night, # num of night
            self.type_of_tour,  # type of tour
        ]
        df = pd.DataFrame([predict_data])

        return (True, time_travel_model.flight_time, time_travel_model.driving_time) if predict_vihicles.model.predict(df) == ['Yes'] else (False, time_travel_model.flight_time, time_travel_model.driving_time)

    def get_n_places(self, num_of_day_spending, driving_time, money, total_province, is_last_province): # get number of places we should visit
        predict_n_places = self.ml_service.get_predict_n_places_model()
        predict_data = [
            num_of_day_spending, # num of days spending in one province
            driving_time, # driving time to one province
            money, # money
            total_province, #total province
            is_last_province # is last province
        ]
        df = pd.DataFrame([predict_data])
        pred = predict_n_places.model.predict(df)
        return pred

    def get_minium_spanning_tree(self, data):
        from scipy.sparse.csgraph import minimum_spanning_tree, breadth_first_order
        mstree = minimum_spanning_tree(data)
        return breadth_first_order(mstree, i_start=0, directed=False, return_predecessors=False)
    
    def to_distance_matrix(self, list_cities: list):
        province_distance_matrix = []
        for city in list_cities:
            city_distance = []
            city_cord = util.get_lat_lon([city])[0]
            for to_city in list_cities:
                to_city_cord = util.get_lat_lon([to_city])[0]
                city_distance.append(util.get_distance_between_two_cord(city_cord, to_city_cord))
            province_distance_matrix.append(city_distance)
        return province_distance_matrix
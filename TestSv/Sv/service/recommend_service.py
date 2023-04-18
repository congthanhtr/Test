from random import sample
import time
from .ml_service import MachineLearningService
from .time_travel import TimeTravelService
from ..myutils import util

from pymongo.database import Database
import pandas as pd

from ..model.recommend_model import RecommendModel, TourProgramModel
from ..model.hotel_model import HotelModel
from ..model.interesting_places import InterestingPlace

class RecommendService:
    num_of_day: int = 0
    num_of_night: int = 0
    cities_from: list = []
    cities_to: list = []
    code_cities_from: list = []
    code_cities_to: list = []
    type_of_tour: int = 0
    cost_range: float = 0.0
    contains_ticket: bool = False
    hotel_filter_condition: list = []
    tour_filter_condition: list = []

    ml_service: MachineLearningService = None
    time_travel_service: TimeTravelService = None

    db: Database = None

    NUM_OF_HOTEL_FROM_RESPONSE = 2

    def __init__(
        self,
        num_of_day: int,
        num_of_night: int,
        cities_from: list,
        cities_to: list,
        type_of_tour: int,
        cost_range: float,
        contains_ticket: bool,
        db: Database,
        hotel_filter_condition = None,
        tour_filter_condition = None,
        ml_service = None,
        time_travel_service = None,
    ) -> None:
        self.num_of_day = num_of_day
        self.num_of_night = num_of_night

        # transform city code to string
        self.code_cities_from = cities_from
        self.cities_from = []
        for cf in cities_from:
            self.cities_from.append(util.get_province_name_by_code(cf))

        self.code_cities_to = cities_to
        self.cities_to = []
        for ct in cities_to:
            self.cities_to.append(util.get_province_name_by_code(ct))

        self.type_of_tour = type_of_tour
        self.cost_range = cost_range
        self.contains_ticket = contains_ticket
        self.hotel_filter_condition = hotel_filter_condition
        self.tour_filter_condition = tour_filter_condition

        self.ml_service = ml_service
        self.time_travel_service = time_travel_service

        self.db = db

    def recommend_v3(self): # change predict vehicle model
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

        collection_poi = self.db.get_collection('vn_pois')
        collection_driving_time = self.db.get_collection('vn_provinces_driving_time')
        collection_hotel = self.db.get_collection('vn_hotels')
        
        # calculate total travel time with predicted transport
        time_travel_service = self.time_travel_service.calculate_time_travel(self.cities_from, self.cities_to, collection=collection_driving_time)
        predict_transport_data = self.preprocess_data_for_predict_transport(time_travel_service)
        predict_transport_model = self.ml_service.get_predict_transport_model()
        transport = predict_transport_model.model.predict(predict_transport_data)[0]
        recommend_model.main_transport = transport
        total_travel_time = self.get_total_travel_time(time_travel_service, transport)

        # get distance matrix from cities_from
        list_cities_to_cord = []
        for city in self.cities_to:
            city_cord = util.get_lat_lon([city])
            list_cities_to_cord.extend(city_cord)
        self.cities_to = self.to_travel_order(self.cities_to, list_cities_to_cord)

        # divide equally time to each province
        list_travel_time_by_each_province = util.divide_equally(self.num_of_day, len(self.cities_to))

        # get list hotel
        list_hotel_by_each_province: list[list[HotelModel]] = []
        '''
        [
            [HNhotel1, HNhotel2],
            [BNHoltel1, BNHotel2]
        ]
        '''
        hotel_filter = None
        if self.hotel_filter_condition and len(self.tour_filter_condition) > 0:
            tour_filter = '|'.join(self.tour_filter_condition)
            tour_filter = f'[{tour_filter}]'
        for city in self.cities_to:
            condition = {}
            condition['province_name'] = util.preprocess_city_name(city=city)
            if hotel_filter:
                condition['kinds'] = {
                    '$regex': hotel_filter
                }
            else:
                condition['kinds'] = {
                    '$regex': 'other_hotels'
                }
            collection_hotel_filter = collection_hotel.find(condition)
            hotels = util.get_hotel_list_from_city_name_v2(collection_hotel_filter)
            hotels = sample(hotels, self.NUM_OF_HOTEL_FROM_RESPONSE) 
            list_hotel_by_each_province.append(hotels)
        
        # get list pois by hotel
        list_pois_by_hotel: list[list[list[InterestingPlace]]] = []
        '''
        [
           [
               [hnhotel1_poi1,hnhotel1_poin],
               [hnhotel2_poi1,hnhotel2_poin]
           ],
           [
               [bnhotel1_poi1,bnhotel1_poin],
               [bnhotel2_poi1,bnhotel2_poin]
           ]
        ]
        '''
        tour_filter = None
        if self.tour_filter_condition and len(self.tour_filter_condition) > 0:
            tour_filter = '|'.join(self.tour_filter_condition)
            tour_filter = f'[{tour_filter}]'

        for hotel_in_province in list_hotel_by_each_province:
            list_pois_by_hotel_in_province = []
            cities_to_index = list_hotel_by_each_province.index(hotel_in_province)
            for hotel in hotel_in_province:
                condition = {}
                condition['province_name'] = util.preprocess_city_name(self.cities_to[cities_to_index])
                if tour_filter:
                    condition['kinds'] = {
                        '$regex': tour_filter
                    }
                colelction_tour_filter = collection_poi.find(condition)
                pois = util.get_list_poi_by_cord_v3(hotel.get_cord(), list_poi=colelction_tour_filter)
                list_pois_by_hotel_in_province.append(pois)
            list_pois_by_hotel.append(list_pois_by_hotel_in_province)

        # build program tour again
        list_travel_time_between_provinces = [total_travel_time]
        if len(self.cities_to) > 1:
            for f in range(1, len(self.cities_to)):
                driv_time = self.time_travel_service._calculate_driving_time(collection=collection_driving_time,
                                                                             city_from=self.cities_to[f-1],
                                                                             city_to=self.cities_to[f])
                list_travel_time_between_provinces.append(driv_time)
        
        # build tour program tour again
        for i in range(0, self.NUM_OF_HOTEL_FROM_RESPONSE):
            program_day = []
            no_of_day = 1
            for j in range(0, len(self.cities_to)):
                is_last_province = 1 if j == (len(self.cities_to) - 1) else 0
                driving_time_between_province = list_travel_time_between_provinces[j] if not is_last_province else list_travel_time_between_provinces[j] + self.time_travel_service._calculate_driving_time(collection=collection_driving_time,
                                                                                                                                                                                                            city_from=self.cities_to[j],
                                                                                                                                                                                                            city_to=self.cities_from[0])
                n_places = round(self.get_n_places(list_travel_time_by_each_province[j], driving_time_between_province, self.cost_range, len(self.cities_to), is_last_province)[0])
                n_places_each_day = util.divide_equally(n_places, list_travel_time_by_each_province[j])
                hotel_inday =list_hotel_by_each_province[j][i]
                pois_inday = list_pois_by_hotel[j][i]
                for k in range(0, len(n_places_each_day)):
                    tour_program = TourProgramModel()
                    tour_program.no_of_day = no_of_day
                    tour_program.province = self.cities_to[j]
                    tour_program.hotel = hotel_inday
                    tour_program.pois = []
                    if len(pois_inday) > n_places_each_day[k]:
                        sub_pois = sample(pois_inday, n_places_each_day[k])
                    else:
                        sub_pois = pois_inday.copy() 

                    list_sub_pois_coord = []
                    for poi in sub_pois:
                        list_sub_pois_coord.append(poi.get_cord())
                    tour_program.pois = self.to_travel_order(sub_pois, list_sub_pois_coord)
                    program_day.append(tour_program)
                    no_of_day += 1
                    pois_inday = list(set(pois_inday) - set(sub_pois))
            recommend_model.program.append(program_day)

        # predict places
        return recommend_model
    
    def recommend_v2(self):
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
        collection_driving_time = self.db.get_collection('vn_provinces_driving_time')
        time_travel_service = self.time_travel_service.calculate_time_travel(self.cities_from, self.cities_to, collection=collection_driving_time)
        predict_transport_data = self.preprocess_data_for_predict_transport(time_travel_service)
        transport_model = self.ml_service.get_predict_transport_model()
        transport = transport_model.model.predict(predict_transport_data)[0]
        recommend_model.main_transport = transport

        # get distance matrix from cities_from
        list_cities_to_cord = []
        for city in self.cities_to:
            city_cord = util.get_lat_lon([city])
            list_cities_to_cord.extend(city_cord)
        self.cities_to = self.to_travel_order(self.cities_to, list_cities_to_cord)
        # predict vihicles
        list_travel_time_by_each_vihicle = [] # contains time to go by each vihicle (plane, car,...)
        travel_by_plane, flight_time, driving_time = self.should_travel_by_plane(self.cities_from, self.cities_to)
        if travel_by_plane:        
            list_travel_time_by_each_vihicle.extend([flight_time, driving_time])
        else:
            list_travel_time_by_each_vihicle.extend([driving_time])

        # divide equally time to each province
        list_travel_time_by_each_province = util.divide_equally(self.num_of_day, len(self.cities_to))

        # get list hotel
        list_hotel_by_each_province: list[list[HotelModel]] = []
        '''
        [
            [HNhotel1, HNhotel2],
            [BNHoltel1, BNHotel2]
        ]
        '''
        hotel_filter = None
        if self.hotel_filter_condition and len(self.tour_filter_condition) > 0:
            tour_filter = '|'.join(self.tour_filter_condition)
            tour_filter = f'[{tour_filter}]'
        if not hotel_filter:
            hotel_filter = 'other_hotels'
        for city in self.cities_to:
            condition = {}
            condition['province_name'] = util.preprocess_city_name(city=city)
            if hotel_filter:
                condition['kinds'] = {
                    '$regex': hotel_filter
                }
            else:
                condition['kinds'] = {
                    '$regex': 'other_hotels'
                }
            collection_hotel = self.db.get_collection('vn_hotels').find(condition)
            hotels = util.get_hotel_list_from_city_name_v2(collection_hotel)
            hotels = sample(hotels, self.NUM_OF_HOTEL_FROM_RESPONSE) 
            list_hotel_by_each_province.append(hotels)

        # get list pois by hotel
        list_pois_by_hotel: list[list[list[InterestingPlace]]] = []
        '''
        [
           [
               [hnhotel1_poi1,hnhotel1_poin],
               [hnhotel2_poi1,hnhotel2_poin]
           ],
           [
               [bnhotel1_poi1,bnhotel1_poin],
               [bnhotel2_poi1,bnhotel2_poin]
           ]
        ]
        '''
        tour_filter = None
        if self.tour_filter_condition and len(self.tour_filter_condition) > 0:
            tour_filter = '|'.join(self.tour_filter_condition)
            tour_filter = f'[{tour_filter}]'

        for hotel_in_province in list_hotel_by_each_province:
            list_pois_by_hotel_in_province = []
            cities_to_index = list_hotel_by_each_province.index(hotel_in_province)
            for hotel in hotel_in_province:
                condition = {}
                condition['province_name'] = util.preprocess_city_name(self.cities_to[cities_to_index])
                if tour_filter:
                    condition['kinds'] = {
                        '$regex': tour_filter
                    }
                collection_poi = self.db.get_collection('vn_pois').find(condition)
                pois = util.get_list_poi_by_cord_v3(hotel.get_cord(), list_poi=collection_poi)
                list_pois_by_hotel_in_province.append(pois)
            list_pois_by_hotel.append(list_pois_by_hotel_in_province)

        # build program tour
        for i in range(0, len(list_travel_time_by_each_vihicle)):
            # get list travel time (like travel time from A to B (minutes), B to C,...)
            list_travel_time_between_provinces = [] 
            list_travel_time_between_provinces.append(list_travel_time_by_each_vihicle[i])
            if len(self.cities_to) > 1:
                for f in range(1, len(self.cities_to)):
                    city_a_cord = util.get_lat_lon([self.cities_to[f-1]])[0]
                    city_b_cord = util.get_lat_lon([self.cities_to[f]])[0]
                    dist = util.get_distance_between_two_cord(city_a_cord, city_b_cord)
                    driv_time = self.time_travel_service._calculate_driving_time(dist)
                    list_travel_time_between_provinces.append(driv_time) 
            
            program = []
            for j in range(0, self.NUM_OF_HOTEL_FROM_RESPONSE):
                program_day = []
                no_of_day = 1
                for k in range(0, len(self.cities_to)):
                    is_last_province = 1 if k == (len(self.cities_to) - 1) else 0
                    driving_time_between_province = list_travel_time_between_provinces[i] if not is_last_province else list_travel_time_between_provinces[k] + list_travel_time_by_each_vihicle[i]
                    # get num of places that we will visit in each province
                    n_places = round(self.get_n_places(list_travel_time_by_each_province[k], driving_time_between_province, self.cost_range, len(self.cities_to), is_last_province)[0]) 
                    # ex: 5
                    n_places_each_day = util.divide_equally(n_places, list_travel_time_by_each_province[k]) # num of places that we will visit each day in that province
                    # ex [3, 2]
                    hotel_inday = list_hotel_by_each_province[k][j]
                    pois_inday = list_pois_by_hotel[k][j]
                    # pois_inday = util.get_list_poi_by_cord(hotel_inday.get_cord())
                    for l in range(0, len(n_places_each_day)):
                        tour_program = TourProgramModel()
                        tour_program.no_of_day = no_of_day
                        tour_program.province = self.cities_to[k]
                        tour_program.hotel = hotel_inday
                        tour_program.pois = []
                        # region to travel order
                        #   get random n points that near the hotel
                        if len(pois_inday) > n_places_each_day[l]:
                            sub_pois = sample(pois_inday, n_places_each_day[l])
                        else:
                            sub_pois = pois_inday.copy()
                        #   to list coord
                        list_sub_pois_coord = []
                        for poi in sub_pois:
                            list_sub_pois_coord.append(poi.get_cord())
                        #   call to get travel order
                        tour_program.pois = self.to_travel_order(sub_pois, list_sub_pois_coord)
                        # travel_order = self.to_travel_order(sub_pois, list_sub_pois_coord)
                        # for travel in travel_order:
                        #     tour_program.pois.append(util.get_poi_detail(travel.xid))
                        # endregion
                        program_day.append(tour_program)
                        no_of_day += 1
                        pois_inday = list(set(pois_inday) - set(sub_pois))
                program.append(program_day)
            recommend_model.program.append(program)

        # predict places
        return recommend_model

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
        list_cities_to_cord = []
        for city in self.cities_to:
            city_cord = util.get_lat_lon([city])
            list_cities_to_cord.extend(city_cord)
        province_distance_matrix = self.to_distance_matrix(list_cities_to_cord)
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

        # get list hotel
        list_hotel_by_each_province: list[list[HotelModel]] = []
        #[
        #       [HNhotel1, HNhotel2],
        #       [BNHoltel1, BNHotel2]
        #]
        for city in self.cities_to:
            hotels = util.get_hotel_list_from_city_name(city)
            hotels = sample(hotels, self.NUM_OF_HOTEL_FROM_RESPONSE) 
            list_hotel_by_each_province.append(hotels)
        # get list pois by hotel
        list_pois_by_hotel: list[list[list[InterestingPlace]]] = []
        #[
        #   [
        #       [hnhotel1_poi1,hnhotel1_poin],
        #       [hnhotel2_poi1,hnhotel2_poin]
        #   ],
        #   [
        #       [bnhotel1_poi1,bnhotel1_poin],
        #       [bnhotel2_poi1,bnhotel2_poin]
        #   ]
        # ]
        for hotel_in_province in list_hotel_by_each_province:
            list_pois_by_hotel_in_province = []
            for hotel in hotel_in_province:
                pois = util.get_list_poi_by_cord_v2(hotel.get_cord())
                list_pois_by_hotel_in_province.append(pois)
            list_pois_by_hotel.append(list_pois_by_hotel_in_province)

        # build program tour
        for travel_time in list_travel_time_by_each_vihicle:
            if travel_time == 0:
                continue

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
            
            program = []
            for i in range(0, len(self.cities_to)):
                is_last_province = 1 if i == (len(self.cities_to) - 1) else 0
                driving_time_between_province = list_travel_time_between_provinces[i] if not is_last_province else list_travel_time_between_provinces[i] + travel_time
                # get num of places that we will visit in each province
                n_places = round(self.get_n_places(list_travel_time_by_each_province[i], driving_time_between_province, self.cost_range, len(self.cities_to), is_last_province)[0]) 
                # ex: 5
                n_places_each_day = util.divide_equally(n_places, list_travel_time_by_each_province[i]) # num of places that we will visit each day in that province
                # ex: [3, 2]
                for j in range(0, len(list_hotel_by_each_province)):
                    no_of_day = j + 1
                    hotel_inday = list_hotel_by_each_province[i][j]
                    pois_inday = list_pois_by_hotel[i][j]
                    for k in range(0, len(n_places_each_day)):
                        tour_program = TourProgramModel()
                        tour_program.province = self.cities_to[i]
                        tour_program.no_of_day = no_of_day
                        tour_program.pois = sample(pois_inday, n_places_each_day[k])
                        tour_program.hotel = hotel_inday
                        program.append(tour_program)
                # region temp comment
                # for k in range(0, len(list_hotel_by_each_province[i])):
                #     no_of_day = 1 # day no.1 2 3...
                #     list_pois_inday = list_pois_by_hotel[i][k]
                #     for j in range(0, len(n_places_each_day)):
                #         tour_program = TourProgramModel()
                #         tour_program.province = self.cities_to[i]
                #         tour_program.no_of_day = no_of_day
                #         # request to get n_places_each_day[i] places
                #         # tour_program.pois = ['1' for k in range(0, n_places_each_day[j])]
                #         tour_program.pois = sample(list_pois_inday, n_places_each_day[j])
                #         program.append(tour_program)
                #         no_of_day += 1
                # endregion
            recommend_model.program.append(program)

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
        mstree = minimum_spanning_tree(data).toarray()
        return breadth_first_order(mstree, i_start=0, directed=False, return_predecessors=False)
    
    def get_path_dijkstra(self, data):
        from scipy.sparse.csgraph import dijkstra, breadth_first_order
        mstree = dijkstra(data)
        return breadth_first_order(mstree, i_start=0, directed=False, return_predecessors=False)
    
    def get_path_tsp(self, data):
        from python_tsp.exact import solve_tsp_dynamic_programming
        permutaion, distance = solve_tsp_dynamic_programming(data)
        return permutaion 
    
    def to_distance_matrix(self, list_cord: list):
        province_distance_matrix = []
        for city in list_cord:
            city_distance = []
            for to_city in list_cord:
                city_distance.append(util.get_distance_between_two_cord(city, to_city))
            province_distance_matrix.append(city_distance)
        import numpy as np
        return np.array(province_distance_matrix)
    
    def to_travel_order(self, source, list_cord_of_source):
        if len(source) <= 2:
            return source
        mstree = self.get_path_tsp(self.to_distance_matrix(list_cord_of_source))
        temp = []
        for node in mstree:
            temp.append(source[node])
        return temp
    
    def preprocess_data_for_predict_transport(self, time_travel_service):
        distance = time_travel_service.distance
        flight_time = time_travel_service.flight_time
        driving_time = time_travel_service.driving_time

        list_provinces_has_train = [province['admin_name'] for province in self.db.get_collection('vn_provinces').find({
            'has_train': True
        }, {
            'admin_name': 1,
            '_id': 0
        })]
        if self.cities_from[0] in list_provinces_has_train and self.cities_to[0] in list_provinces_has_train:
            railway_time = time_travel_service.railway_time
        else:
            railway_time = 0

        # (num_of_day  price  contains_ticket  distance  driving_time  flight_time  railway_time)
        return pd.DataFrame([[self.num_of_day, self.cost_range, self.contains_ticket, distance, driving_time, flight_time, railway_time]])
    
    def get_total_travel_time(self, time_travel_service, transport):
        if util.is_equals(transport, 'ô tô'):
            return time_travel_service.driving_time
        if util.is_equals(transport, 'máy bay'):
            return time_travel_service.flight_time
        if util.is_equals(transport, 'tàu hỏa'):
            return time_travel_service.railway_time

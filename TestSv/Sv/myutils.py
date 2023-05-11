import json
from math import pi, cos, asin, sqrt

import pickle
from random import sample
import time
from django.conf import settings
import jsonpickle
import pandas as pd
import requests
import urllib.parse

from geopy import distance

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from .model.vietnam_city_geo import VietnamCityGeo, VietnamCityBBox, VietnamAirport
from .model.hotel_model import HotelModel
from .model.interesting_places import InterestingPlace

class util:

    API_KEY = open('static/api_key.txt').read()
    API_KEY_OPENTRIPMAP = open('static/api_key_opentripmap.txt').read()
    
    NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE = 'not supported this http method'
    EXCEPTION_THROWN_AT_JSONRESPONSE = 'exception thrown at '
    EXCEPTION_MESSAGE_JSONRESPONSE = ''
    LOREM = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis vitae eleifend arcu. Ut quis neque ante. Vestibulum ac condimentum tortor, quis mattis metus. Integer in urna et turpis elementum condimentum. Sed bibendum rhoncus fermentum. Nunc viverra dapibus massa, vitae consectetur mauris porttitor sed. Fusce sit amet lorem justo'
    PREVIEW = {
        'source': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4x1GejWnBjnBOw8PoiXpncEWqKJe0oLYX4g&usqp=CAU'
    }
    MAXIUM_DISTANCE_FROM_HOTEL_TO_POI = 50

    vietnam_city_geo = VietnamCityGeo().load_list()
    vietnam_city_bbox = VietnamCityBBox().load_list()
    vietnam_airport = VietnamAirport().load_list()

    NOMINATIM_API = 'https://nominatim.openstreetmap.org/search/{}?format=json&addressdetails=1&countrycodes=vn'
    NOMINATIM_CHECK_API = 'https://nominatim.openstreetmap.org/status.php?format=json'
    NOMINATIM_DETAIL_API = 'https://nominatim.openstreetmap.org/details.php?osmtype={}&osmid={}&format=json'

    OPENTRIPMAP_API = 'https://api.opentripmap.com/0.1/en/places/bbox?lon_min={}&lon_max={}&lat_min={}&lat_max={}&format=json&src_attr=osm&limit={}&apikey={}' # must format with {lonmin, lonmax, latmin, latmax, maxobject, apikey}
    OPENTRIPMAP_DETAIL_PLACE_API = 'https://api.opentripmap.com/0.1/en/places/xid/{}?apikey={}'
    OPENTRIPMAP_HOTELS_API = 'https://api.opentripmap.com/0.1/en/places/radius?radius=50000&lon={}&lat={}&kinds=other_hotels&limit=20&apikey={}'
    OPENTRIPMAP_POI_API = 'https://api.opentripmap.com/0.1/en/places/radius?radius=50000&lon={}&lat={}&kinds={}&limit=20&apikey={}'
    
    @staticmethod
    def get_exception(at: str, msg: str) -> dict:
        '''
        get exception and return it as msg to client
        '''
        util.EXCEPTION_THROWN_AT_JSONRESPONSE += at
        util.EXCEPTION_MESSAGE_JSONRESPONSE = str(msg)
        return {
            'ex_at': util.EXCEPTION_THROWN_AT_JSONRESPONSE,
            'ex_msg': util.EXCEPTION_MESSAGE_JSONRESPONSE
        }

    #region topsis method
    @staticmethod
    def Calc_Values(temp_dataset, nCol, impact):
        # print(" Calculating Positive and Negative values...\n")
        p_sln = (temp_dataset.max().values)[0:]
        n_sln = (temp_dataset.min().values)[0:]
        for i in range(0, nCol):
            if impact[i] == '-':
                p_sln[i], n_sln[i] = n_sln[i], p_sln[i]
        return p_sln, n_sln

    def Normalize(temp_dataset, nCol, weights):
        # normalizing the array
        # print(" Normalizing the DataSet...\n")
        for i in range(0, nCol):
            temp = 0
            for j in range(len(temp_dataset)):
                temp = temp + temp_dataset.iloc[j, i]**2
            temp = temp**0.5
            for j in range(len(temp_dataset)):                      
                temp_dataset.iat[j, i] = (
                    temp_dataset.iloc[j, i] / temp)*weights[i]
        return temp_dataset

    def topsis_pipy(temp_dataset, dataset, nCol, weights, impact):
        # normalizing the array
        temp_dataset = util.Normalize(temp_dataset, nCol, weights)

        # Calculating positive and negative values
        p_sln, n_sln = util.Calc_Values(temp_dataset, nCol, impact)

        # calculating topsis score
        # print(" Generating Score and Rank...\n")
        score = []
        for i in range(len(temp_dataset)):
            temp_p, temp_n = 0, 0
            for j in range(0, nCol):
                temp_p = temp_p + (p_sln[j] - temp_dataset.iloc[i, j])**2
                temp_n = temp_n + (n_sln[j] - temp_dataset.iloc[i, j])**2
            temp_p, temp_n = temp_p**0.5, temp_n**0.5
            score.append(temp_n/(temp_p + temp_n))
        dataset['Topsis Score'] = score

        # calculating the rank according to topsis score
        dataset['Rank'] = (dataset['Topsis Score'].rank(
            method='max', ascending=False))
        dataset = dataset.astype({"Rank": int})
        return dataset
        #endregion

    # @staticmethod
    # def searchForLocation(address):
    #     '''
    #     Parameters:
    #         address: String
    #             - The address is a user input.

    #     Returns:
    #         location: Dictionary
    #             - A dictionary returning the latitude, and longitude
    #             of an address.
    #     '''

    #     gmaps = googlemaps.Client(key=util.api_key)
    #     #geocoding and address
    #     geocodeResult = gmaps.geocode(address)

    #     if geocodeResult:
    #         location = geocodeResult[0]['geometry']['location']
    #         return location

    @staticmethod
    def searchForLocation_v2(address):
        '''
        Parameters:
            address: String
                - The address is a user input.

        Returns:
            location: Dictionary
                - A dictionary returning the latitude, and longitude
                of an address.
        '''
        url = util.NOMINATIM_API.format(address)
        response = requests.get(url).json()
        if response:
            location = response[0]
            # return {'lat': location['lat'], 'lng': location['lon']}
            return (float(location['lat']), float(location['lon']))
            # return location
    
    @staticmethod
    def search_for_boundary_box(address):
        '''
        Tìm thông tin về boundary box thông qua address
            Trả về: tuple (lonmin, lonmax, latmin, latmax)
        '''
        response = requests.get(util.NOMINATIM_API.format(address)).json()
        if response:
            location = response[0]['boundingbox']
            return (location[2], location[3], location[0], location[1])

    @staticmethod
    def to_json(obj: object):
        '''
        transform data into json to send to client
        '''
        encoded_data = jsonpickle.encode(obj, unpicklable=False)
        decoded_data = jsonpickle.decode(encoded_data)
        return decoded_data

    @staticmethod
    def contains_day(source: str, no_of_day: int):
        day_with_zero = 'ngày 0' + str(no_of_day)
        day_without_zero = 'ngày ' + str(no_of_day)
        if source.lower().__contains__(day_with_zero):
            return (True, day_with_zero)
        elif source.lower().__contains__(day_without_zero):
            return (True, day_without_zero)
        else:
            return (False, '')
        
    @staticmethod
    def find_between_element(first_element: WebElement, second_element: WebElement):
        """
        Tìm tất cả các element nằm giữa first và second element 
        """
        if first_element is not None and second_element is not None:
            after = first_element.find_elements(By.XPATH, 'following-sibling::*')
            before = second_element.find_elements(By.XPATH, 'preceding-sibling::*')
            middle = [elem for elem in after if elem in before]
        elif first_element is None:
            middle = second_element.find_elements(By.XPATH, 'preceding-sibling::*')
        elif second_element is None:
            middle = first_element.find_elements(By.XPATH, 'following-sibling::*')
        return middle
    
    @staticmethod
    def is_contains(source: str, child: str):
        """
        Kiểm tra xem chuỗi source có bao gồm chuỗi child không?
            Trả về: True nếu chứa, False nếu không
        """
        if source.lower().__contains__(child.lower()):
            return True
        return False
    
    @staticmethod
    def is_equals(source: str, des: str):
        if source.lower() == des.lower():
            return True
        return False
    
    @staticmethod
    def is_null_or_empty(source: str):
        """
        Kiểm tra chuỗi None hay chuỗi trống hay không?
        """
        if source == '' or source is None:
            return True
        return False
    
    @staticmethod
    def find_city_for_destination(destination: str):
        """
        Tìm tỉnh/thành phố cho địa điểm du lịch
        """
        response = requests.get(util.NOMINATIM_API.format(urllib.parse.quote(destination))).json()
        if response:
            address = response[0]['address']
            city: str = ''
            if 'state' in address:
                city = address['state']
            if 'city' in address:
                city = address['city']
            return city
    
    @staticmethod
    def get_boundary_box(address: str):
        index = util.vietnam_city_bbox.list_id.index(address)
        return (
            util.vietnam_city_bbox.list_min_lon[index],
            util.vietnam_city_bbox.list_max_lon[index],
            util.vietnam_city_bbox.list_min_lat[index],
            util.vietnam_city_bbox.list_max_lat[index],
        )
    
    @staticmethod
    def get_list_interesting_places(addresses: list[str], limit: int) -> list:
        '''
        Tìm thông tin về các địa điểm tham quan du lịch hấp dẫn tại một điểm
        '''
        list_interesting_places = []
        for address in addresses:
            boundary_box = util.get_boundary_box(address=address)
            url = util.OPENTRIPMAP_API.format(boundary_box[0], boundary_box[1], boundary_box[2], boundary_box[3], limit, util.API_KEY_OPENTRIPMAP)
            response = requests.get(url=url)
            if not response.raise_for_status():
                response = response.json()
                for poi in response:
                    xid = poi['xid']
                    detail_url = util.OPENTRIPMAP_DETAIL_PLACE_API.format(xid, util.API_KEY_OPENTRIPMAP)
                    detail_response = requests.get(detail_url)
                    if (not detail_response.raise_for_status()):
                        detail_response = detail_response.json()
                        # get value
                        en_summary = ''
                        en_name = ''
                        image = ''
                        if 'wikipedia_extracts' in detail_response:
                            en_summary = detail_response['wikipedia_extracts']['text']
                        if 'name' in detail_response:
                            en_name = detail_response['name']
                        if 'image' in detail_response:
                            image = detail_response['image']
                        # assign value
                        interesting = InterestingPlace()
                        # interesting.summary = util.translate_to_vietnamese(en_summary)
                        interesting.summary = en_summary
                        # interesting.vi_name = util.translate_to_vietnamese(en_name)
                        interesting.vi_name = en_name
                        interesting.image = image
                        interesting.province = address
                        # append to list
                        list_interesting_places.append(interesting)
        return list_interesting_places
    
    @staticmethod
    def get_list_poi_by_cord(cord: tuple, filter_tour: list = None):
        list_poi = []
        url = util.OPENTRIPMAP_POI_API.format(cord[1], cord[0], 'interesting_places', util.API_KEY_OPENTRIPMAP)
        response = requests.get(url=url)
        if not response.raise_for_status():
            pois = response.json()['features']
            for poi in pois:
                properties = poi['properties']
                geometry = poi['geometry']
                if not util.is_null_or_empty(properties['name']):
                    list_poi.append(InterestingPlace(
                        vi_name=properties['name'],
                        lat=geometry['coordinates'][1],
                        lng=geometry['coordinates'][0]
                    ))
        
        return list_poi
    
    @staticmethod
    def get_list_poi_by_cord_v2(cord: tuple, filter_tour: list = None):
        list_poi = []
        url = util.OPENTRIPMAP_POI_API.format(cord[1], cord[0], 'interesting_places', util.API_KEY_OPENTRIPMAP)
        response = requests.get(url=url)
        if not response.raise_for_status():
            pois = response.json()['features']
            for poi in pois:
                properties = poi['properties']
                geometry = poi['geometry']
                if not util.is_null_or_empty(properties['name']):
                    list_poi.append(InterestingPlace(
                        xid=properties['xid'],
                        vi_name=properties['name'],
                        lat=geometry['coordinates'][1],
                        lng=geometry['coordinates'][0]
                    ))
        
        return list_poi
    
    @staticmethod
    def get_list_poi_by_cord_v3(cord: tuple, list_poi: list = None, filter_tour: list = None): # get list from by db
        # list_pois = [InterestingPlace(
        #     vi_name=poi['vi_name'],
        #     xid=poi['xid'],
        #     lat=poi['point']['lat'],
        #     lng=poi['point']['lon'],
        #     description=poi['vi_description'] if 'vi_description' in poi else util.LOREM,
        #     preview=poi['preview']
        # ) for poi in list_poi if util.get_distance_between_two_cord(cord, InterestingPlace(vi_name=poi['vi_name'],
        #     xid=poi['xid'],
        #     lat=poi['point']['lat'],
        #     lng=poi['point']['lon'],
        #     description=poi['description'],
        #     preview=poi['preview']).get_cord()) < util.MAXIUM_DISTANCE_FROM_HOTEL_TO_POI]
        
        # list_pois = []
        # for poi in list_poi:
        #     a_poi = InterestingPlace(
        #         vi_name=poi['vi_name'],
        #         xid=poi['xid'],
        #         lat=poi['point']['lat'],
        #         lng=poi['point']['lon'],
        #         description=poi['vi_description'] if 'vi_description' in poi else util.LOREM,
        #         preview=poi['preview'] if poi['preview'] is not None else util.PREVIEW
        #     )
        #     if util.get_distance_between_two_cord(cord, a_poi.get_cord()) < util.MAXIUM_DISTANCE_FROM_HOTEL_TO_POI:
        #         list_pois.append(a_poi)
        # return list_pois

        list_pois = [InterestingPlace(
            vi_name=poi['vi_name'],
            xid=poi['xid'],
            lat=poi['point']['lat'],
            lng=poi['point']['lon'],
            description=poi['vi_description'] if 'vi_description' in poi else util.LOREM,
            preview=poi['preview'] if poi['preview'] is not None else util.PREVIEW
        ) for poi in list_poi]
        return list_pois
    
    @staticmethod
    def get_poi_detail(xid: str):
        detail = InterestingPlace()
        url = util.OPENTRIPMAP_DETAIL_PLACE_API.format(xid, util.API_KEY_OPENTRIPMAP)
        response = requests.get(url)
        
        if not response.raise_for_status():
            response = response.json()
            # init default value
            if 'wikipedia_extracts' in response:
                wikipedia_extract = response['wikipedia_extracts']
                detail.description = wikipedia_extract['text']
            if 'point' in response:
                point = response['point']
                detail.lat = point['lat']
                detail.lng = point['lon']
            if 'name' in response:
                detail.vi_name = response['name']
            if 'preview' in response:
                detail.preview = response['preview']
            
        return detail

    @staticmethod
    def get_distance_between_two_cord(cord1: tuple, cord2: tuple):
        # return distance.distance(cord1, cord2).km
        p = pi/180
        a = 0.5 - cos((cord2[0]-cord1[0])*p)/2 + cos(cord1[0]*p) * cos(cord2[0]*p) * (1-cos((cord2[1]-cord1[1])*p))/2
        return 12742 * asin(sqrt(a)) #2*R*asin...
        
    @staticmethod
    def preprocess_city_name(city: str, lower=False):
        import re
        replace_for_province = ['Tỉnh', 'Thành phố']
        big_regex = re.compile('|'.join(map(re.escape, replace_for_province)))
        return big_regex.sub('', city).strip().lower() if lower else big_regex.sub('', city).strip()
    
    @staticmethod
    def get_lat_lon(city: list):
        list_city_geo = []
        try:
            for c in city:
                temp = util.preprocess_city_name(c, True)
                index = util.vietnam_city_geo.list_city_name.index(temp)
                list_city_geo.append((
                    util.vietnam_city_geo.list_lat[index],
                    util.vietnam_city_geo.list_lon[index]
                ))
        except Exception as e:
            print(str(e))
            for c in city:
                    list_city_geo.append(util.searchForLocation_v2(city))
        return list_city_geo

    @staticmethod
    def get_neareast_airport(cord: list):
        list_airport = util.vietnam_airport.load_list_airport()
        neareast_airport = list_airport[0]
        neareast_cord = cord[0]
        list_neareast_airport = []
        for c in cord:
            min_dis = util.get_distance_between_two_cord(c, list_airport[0].get_cord())
            for airport in list_airport:
                dist = util.get_distance_between_two_cord(c, airport.get_cord())
                if dist < min_dis:
                    min_dis = dist
                    neareast_airport = airport
                list_neareast_airport.append(neareast_airport)
        # find the most frequent airport in the list -> neareast airport
        neareast_airport = max(set(list_neareast_airport), key=list_neareast_airport.count)
        min_dis = util.get_distance_between_two_cord(cord[0], neareast_airport.get_cord())
        for c in cord:
            dist = util.get_distance_between_two_cord(c, neareast_airport.get_cord())
            if dist < min_dis:
                min_dis = dist
                neareast_cord = c
        return (neareast_airport, neareast_cord)
    
    @staticmethod
    def get_neareast_airport_v2(cord: list):
        list_airport = util.vietnam_airport.load_list_airport()
        neareast_airport = list_airport[0]
        neareast_cord = neareast_airport.get_cord()
        min_dis = util.get_distance_between_two_cord(cord[0],neareast_airport.get_cord())
        for airport in list_airport:
            dist = util.get_distance_between_two_cord(cord[0], airport.get_cord())
            if dist < min_dis:
                min_dis = dist
                neareast_airport = airport
                neareast_cord = airport.get_cord()
        return (neareast_airport, neareast_cord)

    @staticmethod
    def get_province_name_by_code(code: str):
        from vietnam_provinces.enums import ProvinceEnum
        return ProvinceEnum[f'P_{code}'].value.name
    
    @staticmethod
    def divide_equally(num: int, div: int):
        integer = num // div
        remainder = num % div
        splits = []
        for i in range(div):
            splits.append(integer)
        for i in range(remainder):
            splits[i] += 1
        return splits
    
    @staticmethod
    def get_hotel_list_from_city_name(city: str):
        hotel_list = []
        city_cord = util.get_lat_lon([city])[0]
        url = util.OPENTRIPMAP_HOTELS_API.format(city_cord[1], city_cord[0], util.API_KEY_OPENTRIPMAP)
        response = requests.get(url)
        if not response.raise_for_status():
            hotels = response.json()['features']
            for hotel in hotels:
                properties = hotel['properties']
                geometry = hotel['geometry']
                if not util.is_null_or_empty(properties['name']):
                    hotel_list.append(HotelModel(
                        name=properties['name'],
                        lat=geometry['coordinates'][1],
                        lng=geometry['coordinates'][0]
                    ))
        return hotel_list
    
    @staticmethod
    def get_hotel_list_from_city_name_v2(list_hotels: list): # get hotel list from city in db
        list_hotel = [HotelModel(name=hotel['name'],lat=hotel['lat'],lng=hotel['lng']) for hotel in list_hotels]
        return list_hotel
        
    
    @staticmethod
    def get_db_handle(connection_string=settings.CONNECTION_STRING, db_name=None):
        from pymongo import MongoClient
        client = MongoClient(connection_string)
        db = client[db_name]
        return db

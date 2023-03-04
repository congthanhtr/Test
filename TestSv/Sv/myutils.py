import jsonpickle
import pandas as pd
import os
import sys
import googlemaps

import requests
import urllib.parse

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


class util:

    API_KEY = open('static/api_key.txt').read()
    NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE = {'msg': 'not supported this http method'}
    EXCEPTION_THROWN_AT_JSONRESPONSE = 'exception thrown at '
    EXCEPTION_MESSAGE_JSONRESPONSE = ''

    NOMINATIM_API = 'https://nominatim.openstreetmap.org/search/{}?format=json&addressdetails=1&countrycodes=vn'
    NOMINATIM_CHECK_API = 'https://nominatim.openstreetmap.org/status.php?format=json'
    OPENTRIPMAP_API = 'https://api.opentripmap.com/0.1/en/places/bbox?lon_min={}&lon_max={}&lat_min={}&lat_max={}&format=json&limit={}&apikey={} ' # must format with {lonmin, lonmax, latmin, latmax, maxobject, apikey}

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

    def searchForLocation(address):
        '''
        Parameters:
            address: String
                - The address is a user input.

        Returns:
            location: Dictionary
                - A dictionary returning the latitude, and longitude
                of an address.
        '''

        gmaps = googlemaps.Client(key=util.api_key)
        #geocoding and address
        geocodeResult = gmaps.geocode(address)

        if geocodeResult:
            location = geocodeResult[0]['geometry']['location']
            return location

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
        check_result = requests.get(util.NOMINATIM_CHECK_API).json()
        if check_result['message'] == 'OK':
            url = util.NOMINATIM_API.format(address)
            response = requests.get(url).json()
            if response:
                location = response[0]
                return {'lat': location['lat'], 'lng': location['lon']}
                # return location
        else:
            return check_result['message']
        
    def search_for_boundary_box(address):
        '''
        Tìm thông tin về boundary box thông qua address
            Trả về: tuple (lonmin, lonmax, latmin, latmax)
        '''
        check_result = requests.get(util.NOMINATIM_CHECK_API).json()
        if check_result['message'] == 'OK':
            response = requests.get(util.NOMINATIM_API.format(address)).json()
            if response:
                location = response[0]['boundingbox']
                return (location[2], location[3], location[0], location[1])

    def to_json(obj):
        '''
        transform data into json to send to client
        '''
        encoded_data = jsonpickle.encode(obj, unpicklable=False)
        decoded_data = jsonpickle.decode(encoded_data)
        return decoded_data

    def contains_day(source: str, no_of_day: int):
        day_with_zero = 'ngày 0' + str(no_of_day)
        day_without_zero = 'ngày ' + str(no_of_day)
        if source.lower().__contains__(day_with_zero):
            return (True, day_with_zero)
        elif source.lower().__contains__(day_without_zero):
            return (True, day_without_zero)
        else:
            return (False, '')
        
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
    
    def is_contains(source: str, child: str):
        """
        Kiểm tra xem chuỗi source có bao gồm chuỗi child không?
            Trả về: True nếu chứa, False nếu không
        """
        if source.lower().__contains__(child.lower()):
            return True
        return False
    
    def is_equals(source: str, des: str):
        if source.lower() == des.lower():
            return True
        return False
    
    def is_null_or_empty(source: str):
        """
        Kiểm tra chuỗi None hay chuỗi trống hay không?
        """
        if source == '' or source is None:
            return True
        return False
    
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

    def get_list_interesting_places(address: str, limit: int, apikey = None):
        '''
        Tìm thông tin về các địa điểm tham quan du lịch hấp dẫn tại một điểm
        '''
        boundary_box = util.search_for_boundary_box(address=address)
        apikey = open('static/api_key_opentripmap.txt').read()
        url = util.OPENTRIPMAP_API.format(boundary_box[0], boundary_box[1], boundary_box[2], boundary_box[3], limit, apikey)
        response = requests.get(url).json()
        return response


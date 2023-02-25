import jsonpickle
import pandas as pd
import os
import sys
import googlemaps

import requests
import urllib.parse


class util:

    API_KEY = open('static/api_key.txt').read()
    NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE = {'msg': 'not supported this http method'}
    EXCEPTION_THROWN_AT_JSONRESPONSE = 'exception thrown at '
    EXCEPTION_MESSAGE_JSONRESPONSE = ''

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
        check_url = 'https://nominatim.openstreetmap.org/status.php?format=json'
        check_result = requests.get(check_url).json()
        if check_result['message'] == 'OK':
            url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json&addressdetails=1'
            response = requests.get(url).json()
            if response:
                location = response[0]
                return {'lat': location['lat'], 'lng': location['lon']}
                # return location
        else:
            return check_result['message']

    def to_json(obj):
        '''
        transform data into json to send to client
        '''
        encoded_data = jsonpickle.encode(obj, unpicklable=False)
        decoded_data = jsonpickle.decode(encoded_data)
        return decoded_data

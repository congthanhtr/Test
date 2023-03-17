import json
import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from http import HTTPStatus

from .crawler import Crawler
from .model.weather_forcast import WeatherForecastService
from .model.result_object import ResultObject
from .model.time_travel import TimeTravelService
from .myutils import util

import pandas as pd
import googlemaps
import traceback, sys
from googleplaces import GooglePlaces, types, lang, ranking

# ML models
from .ml_model.decision_tree import model as dc_model

from .ml_model.linear_regression import lm_model

from .ml_model.logistic_regression import lgr_model

# Create your views here.

BASE_API_URL = 'api/v1/'
service = None

def index(request):
    API_ENDPOINT = BASE_API_URL+'index'
    result = ResultObject()
    # region request content
    # endregion
    try:
        crawler = Crawler()
        list_tour = crawler.crawl_tour_detail()
        result.data = list_tour
    except Exception as ex:
        result.data = util.get_exception(API_ENDPOINT, traceback.format_exc())
        result.status_code = HTTPStatus.BAD_REQUEST.value
    return JsonResponse(util.to_json(result))
def maps(request):
    map_client = googlemaps.Client(util.API_KEY)
    location = util.searchForLocation('Đà Lạt') # param from requests
    search_string = 'hotel' # param from request
    distance = 15*1.6
    response = map_client.places_nearby(location=location, keyword=search_string, name='hotel',radius=distance, types=[types])
    result = response.get('results')
    print(result)
    return HttpResponse(result)

def maps_v3(request):
    start = time.time()
    API_ENDPOINT = BASE_API_URL+'maps_v3'
    result = ResultObject()
    if request.method == "POST":
        try:
            body_content = json.loads(request.body)
            address = body_content['address']
            limit = body_content['limit']
            location = util.get_list_interesting_places(addresses=address, limit=limit)
            end = time.time()
            print('total request time: ' + str(end-start))
            result.data = location
            result.status_code = HTTPStatus.OK.value
        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, traceback.format_exc())
    return JsonResponse(util.to_json(result))

def maps_v2(request):
    API_ENDPOINT = BASE_API_URL+'maps_v2'
    if request.method == "POST":
        # region request content
        body_content = json.loads(request.body)
        address = body_content['address']
        types = body_content['types']
        # endregion
        result = ResultObject()
        location = util.searchForLocation_v2(address)
        if type(location) == 'str':
            return JsonResponse(util.to_json(location))
        else:
            google_places = GooglePlaces(util.API_KEY)
            try:
                nearby = google_places.nearby_search(
                    lat_lng=location,
                    radius=10000,
                    types=types,
                    rankby=ranking.PROMINENCE,
                    language=lang.VIETNAMESE
                )
                return JsonResponse(util.to_json(nearby))
            except Exception as e:
                return JsonResponse(util.get_exception(API_ENDPOINT, str(e))) 
    else:
        return JsonResponse(util.get_exception(API_ENDPOINT, util.NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE))

def crawl(request):
    crawler = Crawler()
    list_tour = crawler.crawl(None)
    return JsonResponse({"status": "OK"})

def recommend_tour(request):
    API_ENDPOINT = BASE_API_URL+'recommend_tour'
    if request.method == "POST":
        # get data of hot tour
        try:
            dataset, temp_dataset = pd.read_csv('static/crawl.csv'), pd.read_csv('static/crawl.csv')
        except Exception as e:
            return JsonResponse(util.get_exception(API_ENDPOINT, str(e)))
        # region request content
        body_content = json.loads(request.body)
        list_column_names = body_content['list_column_names']
        weights = body_content['weights']
        impacts = body_content['impacts']
        n_col = body_content['n_col']
        # endregion
        temp_dataset = temp_dataset.filter(list_column_names)
        #region temp
        # all_weight = list(ConfigweightTour.objects.filter(isdeleted=False))
        # all_impact = list(ConfigimpactTour.objects.filter(isdeleted=False))
        # list_column_names = ['TourHotelRate', 'TourPrice']
        # weights = []
        # impacts = []
        # n_col = len(temp_dataset.columns.values)
        # for column_name in list_column_names:
        #     for w in all_weight:
        #         if (w.tourproperty == column_name):
        #             weights.append(w.weight)
        #             break
        #     for i in all_impact:
        #         if i.tourproperty == column_name:
        #             impacts.append("+" if i.tourimpact else "-")
        #             break
        #endregion
        # calculate rank for each tour
        data = util.topsis_pipy(temp_dataset, temp_dataset, n_col, weights, impacts)
        # add column rank to original dataset 
        dataset['Rank'] = data['Rank']
        # sort by rank
        dataset = dataset.sort_values(by='Rank', ascending=True)
        # transfrom dataframe to json
        dataset_dict = dataset.to_dict('records')
        tour_infos = [TourInformation(
            tour_name=data['TourName'],
            tour_code=data['TourCode'],
            tour_length=data['TourLength'],
            tour_from=data['TourFrom'],
            tour_transport=data['TourTransport'],
            tour_hotel_rate=data['TourHotelRate'],
            tour_start_date=data['TourStartDate'],
            tour_price=data['TourPrice'],
            tour_kid=data['TourKid'],
            tour_program=data['TourProgram']
        ) for data in dataset_dict]
        return JsonResponse(util.to_json(tour_infos), safe=False)
        # return HttpResponse(dataset.to_string())
    else:
        return JsonResponse(util.get_exception(API_ENDPOINT, util.NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE))

def weather_forecast(request):
    API_ENDPOINT = BASE_API_URL+'weather_forecast'
    result = ResultObject()
    if request.method == "POST":
        try:
            forecaster = WeatherForecastService()
            # region request content
            body_content = json.loads(request.body)
            latitude = body_content['latitude']
            longitude = body_content['longitude']
            forecast_type = body_content['forecast_type']
            # endregion
            forecast_result = forecaster.do_forecast(latitude, longitude, forecast_type)
            if (forecast_result is None):
                forecast_result = {"msg": "latitude, longitude or forecast_type is invalid"}
                result.assign_value(forecast_result, HTTPStatus.BAD_REQUEST.value)
            else:
                result.assign_value(forecast_result, HTTPStatus.OK.value)
        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, str(traceback.format_exc()))
            result.status_code = HTTPStatus.BAD_REQUEST.value
    else:
        result.data = util.get_exception(API_ENDPOINT, util.NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE)
        result.status_code = HTTPStatus.METHOD_NOT_ALLOWED.value

    return JsonResponse(util.to_json(result))

def time_travel(request):
    API_ENDPOINT =  BASE_API_URL+'time_travel'
    result = ResultObject()
    if request.method == "POST":
        try:
            body_content = json.loads(request.body)
            city_from = body_content['from']
            city_to = body_content['to']
            from vietnam_provinces.enums import ProvinceEnum
            province_from = []
            for f in city_from:
                province_from.append(ProvinceEnum[f'P_{f}'].value.name)
            province_to = []
            for t in city_to:
                province_to.append(ProvinceEnum[f'P_{t}'].value.name)
            time_travel_service = TimeTravelService()
            result.data = time_travel_service.calculate_time_travel(province_from, province_to)
            result.status_code = HTTPStatus.OK.value
        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, str(traceback.format_exc()))
            result.status_code = HTTPStatus.BAD_REQUEST.value
    else:
        result.data = util.get_exception(API_ENDPOINT, util.NOT_SUPPORT_HTTP_METHOD_JSONRESPONSE)
        result.status_code = HTTPStatus.METHOD_NOT_ALLOWED.value

    return JsonResponse(util.to_json(result))

def predict_vehicle(request):
    API_ENDPOINT = BASE_API_URL+'predict_vehicle'
    result = ResultObject()
    if request.method == "POST":
        try:
            data = json.loads(request.body) # Data is an array

            # Load the data into a pandas DataFrame
            df = pd.DataFrame([data['data']])

            y_pred = dc_model.predict(df.values)

            # Convert the predicted labels to a list
            predictions = y_pred.tolist()

            # Create a dictionary with the predicted labels
            resData = result.assign_value(predictions, 200)

        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, str(traceback.format_exc()))
            result.status_code = HTTPStatus.BAD_REQUEST.value  
    # Return the result as a JSON response
    return JsonResponse(util.to_json(resData))


def predict_places(request):
    API_ENDPOINT = BASE_API_URL+'predict_places'
    result = ResultObject()
    if request.method == "POST":
        try:
            data = json.loads(request.body) # Data is an array

            # Load the data into a pandas DataFrame
            df = pd.DataFrame([data['data']])

            y_pred = lm_model.predict(df.values)

            # make y_pred a rounded number
            actualResult = round(y_pred[0])

            # Create a dictionary with the predicted labels
            resData = result.assign_value(actualResult, 200)

        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, str(traceback.format_exc()))
            result.status_code = HTTPStatus.BAD_REQUEST.value  
    # Return the result as a JSON response
    return JsonResponse(util.to_json(resData))

def predict_another_province(request):
    API_ENDPOINT = BASE_API_URL+'predict_another_province'
    result = ResultObject()
    if request.method == "POST":
        try:
            data = json.loads(request.body) # Data is an array

            # Load the data into a pandas DataFrame
            df = pd.DataFrame([data['data']])

            y_pred = lgr_model.predict(df.values)
   

            # Convert the predicted labels to a list
            predictions = y_pred.tolist()[0]

            # Create a dictionary with the predicted labels
            resData = result.assign_value(predictions, 200)

        except Exception as e:
            result.data = util.get_exception(API_ENDPOINT, str(traceback.format_exc()))
            result.status_code = HTTPStatus.BAD_REQUEST.value  
    # Return the result as a JSON response
    return JsonResponse(util.to_json(resData))

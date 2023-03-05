import json
import pickle
import requests


class WeatherForecast:

    frequency_daily: str = "daily"
    frequency_hourly: str = "hourly"
    timezone_auto = "timezone=auto"
    current_weather = "current_weather=true"
    
    temperature_max = "temperature_2m_max"
    temperature_min = "temperature_2m_min"
    temperature_2m = 'temperature_2m'

    longitude = "longitude="
    latitude = "latitude="
    base_url = "https://api.open-meteo.com/v1/forecast?"

    weather_indicate = {
        1: ('Khá quang đãng', True),
        2: ('Nhiều mây', True),
        3: ('Âm u', False),

        45: ('Có sương mù', False),
        48: ('Sương mù đọng lại', False),

        51: ('Mưa phùn nhẹ', True),
        53: ('Mưa phùn vừa', False),
        55: ('Mưa phùn dày đặc', False),

        56: ('Mưa phùn + Rét buốt', False),
        57: ('Mưa phùn dày đặc + Rét buốt', False),
        
        61: ('Mưa nhẹ', True),
        63: ('Mưa vừa', False),
        65: ('Mưa nặng hạt', False),

        66: ('Mưa + Rét buốt', False),
        67: ('Mưa to + Rét buốt', False),

        71: ('Tuyết rơi nhẹ', True), # VN chắc ít -> skip
        73: ('Tuyết rơi vừa', True),

        95: ('Mưa bão nhỏ và vừa', False),

        96: ('Mưa bão kèm theo mưa đá nhỏ', False),
        99: ('Mưa bão kèm theo mưa đá lớn', False)
    }

    def hourly_forecast(self, latitude, longitude):
        # hourly forecast does not need time zone info
        latitude = self.latitude + latitude
        longitude = self.longitude + longitude
        url = (
            self.base_url
            + self.timezone_auto
            + "&"
            + self.current_weather
            + "&"
            + latitude
            + "&"
            + longitude
            + "&"
            + self.frequency_hourly
            + "="
            + self.temperature_2m
        )
        response = requests.get(url=url).json()
        return response

    def daily_forecast(self, latitude, longitude):
        latitude = self.latitude + latitude
        longitude = self.longitude + longitude
        url = (
            self.base_url
            + self.timezone_auto
            + "&"
            + self.current_weather
            + "&"
            + latitude
            + "&"
            + longitude
            + "&"
            + self.frequency_daily
            + "="
            + self.temperature_max
            + ","
            + self.temperature_min
        )
        response = requests.get(url=url).json()
        weathercode = self.weathercode_to_text(response['current_weather']['weathercode'])
        response['current_weather_text'] = weathercode[0]
        response['is_current_weather_good'] = weathercode[1]
        return response

    def weathercode_to_text(self, weathercode):
        return self.weather_indicate[weathercode]


from wikipediaapi import Wikipedia
# import translators as ts

# wiki = Wikipedia('vi')
# lookup = wiki.page('Thác_Pongour') 
# summ = lookup.summary
# print(summ)
# translator = Translator()
# translated = translator.translate(text=summ, dest='en', src='vi')
# print(translated.text)


# print(ts.translate_text(query_text=wiki, translator='google', from_language='vi', to_language='en'))

class VietnamCityGeo:

    list_city_name = []
    list_lat = []
    list_lon = []

    def __init__(self) -> None:
        data = pickle.load(open('TestSv/static/VietnamCityGeo.pickle', mode='rb'))
        self.list_city_name = data.list_city_name
        self.list_lat = data.list_lat
        self.list_lon = data.list_lon

    def read_and_parse(self):
        self.list_city_name = []
        self.list_lat = []
        self.list_lon = []
        text = open('crawl_tour/vn.json', encoding='utf-8').read()
        city_json: list = json.loads(text)
        for city in city_json:
            self.list_city_name.append(city['city'].lower())
            self.list_lat.append(city['lat'].lower())
            self.list_lon.append(city['lng'].lower())
        return self

# test = VietnamCityGeo()
# _test = test.read_and_parse()
# pickle.dump(_test, open('crawl_tour/VietnamCityGeo.pickle', mode='wb'))
# data: VietnamCityGeo =  pickle.load(open('crawl_tour/VietnamCityGeo.pickle', mode='rb'))
# print(len(test.list_city_name))
# print(data.list_city_name[1])
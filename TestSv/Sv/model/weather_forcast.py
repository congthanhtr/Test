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
        0: ('Trời trong', True),

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

    def do_forecast(self, latitude, longitude, forecast_type: str):
        
        if (forecast_type.lower() == 'daily'):
            result = self.daily_forecast(latitude, longitude)
        elif forecast_type.lower() == 'hourly':
            result = self.hourly_forecast(latitude, longitude)
        else:
            result = None
        return result

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

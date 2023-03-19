import json

class VietnamCityModel:
    def load_list(self):
        '''
        load data from file and store at ram
        '''
        pass

class VietnamCityGeo(VietnamCityModel):

    list_city_name = []
    list_lat = []
    list_lon = []

    def load_list(self):
        self.list_city_name = []
        self.list_lat = []
        self.list_lon = []
        text = open('static/vn2.json', encoding='utf-8').read()
        text_json = json.loads(text)
        for city in text_json:
            self.list_city_name.append(city['admin_name'].lower())
            self.list_lat.append(float(city['lat']))
            self.list_lon.append(float(city['lng']))
        return self
    

class VietnamCityBBox(VietnamCityModel):
    list_id = []
    list_min_lon = []
    list_max_lon = []
    list_min_lat = []
    list_max_lat = []

    def load_list(self):
        self.list_id = []
        self.list_min_lon = []
        self.list_max_lon = []
        self.list_min_lat = []
        self.list_max_lat = []
        text = open('static/VietnamCityBBox.json', encoding='utf-8').read()
        text_json = json.loads(text)
        for city in text_json:
            self.list_id.append(city)
            self.list_min_lon.append(str(text_json[city][0]))
            self.list_min_lat.append(str(text_json[city][1]))
            self.list_max_lon.append(str(text_json[city][2]))
            self.list_max_lat.append(str(text_json[city][3]))
        
        return self        


class VietnamAirportModel:
    code: str
    cord: tuple

    def __init__(self, code, lat, lon) -> None:
        self.code = code
        self.cord = (lat, lon)


class VietnamAirport(VietnamCityModel):
    list_code = []
    list_lat = []
    list_lon = []

    def load_list(self):
        self.list_code = []
        self.list_lat = []
        self.list_lon = []
        text = open('static/vn_airports.json', encoding='utf-8').read()
        text_json = json.loads(text)
        for airport in text_json:
            self.list_code.append(airport['code'])
            self.list_lat.append(float(airport['lat']))
            self.list_lon.append(float(airport['lon']))
        
        return self
    
    def load_list_airport(self):
        list_airport: list[VietnamAirportModel] = []
        for i in range(0, len(self.list_code)):
            list_airport.append(VietnamAirportModel(
                self.list_code[i],
                self.list_lat[i],
                self.list_lon[i]
            ))
        return list_airport
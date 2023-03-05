import json


class VietnamCityGeo:

    list_city_name = []
    list_lat = []
    list_lon = []

    def load_list(self):
        self.list_city_name = []
        self.list_lat = []
        self.list_lon = []
        text = open('static/vn.json', encoding='utf-8').read()
        text_json = json.loads(text)
        for city in text_json:
            self.list_city_name.append(city['city'].lower())
            self.list_lat.append(city['lat'])
            self.list_lon.append(city['lng'])
        return self
    

class VietnamCityBBox:
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


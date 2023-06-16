# import
import json
from random import randint, sample
import requests
import datetime
import regex
import os
import time
import traceback

from dotenv import load_dotenv
from pymongo import MongoClient
from vietnam_provinces.enums import ProvinceEnum

# func
def find_ele_in_list_obj_by_prop(list, prop_name, prop_value):
    res = []
    for ele in list:
        prop_value_lower = prop_value.lower()
        elem_lower = ele[prop_name].lower()
        if prop_value_lower in elem_lower or elem_lower in prop_value_lower:
            res.append(ele)
    return res

start = time.time()
print('started...')

# init
client = MongoClient()
recommender = client.recommender
vn_provinces_collection = recommender.vn_provinces

# load env
load_dotenv()
GEOAPIFY_APIKEY = os.getenv('GEOAPIFY_APIKEY')
OPENTRIPMAP_APIKEY = os.getenv('OPENTRIPMAP_APIKEY')

# reading file
list_placeid_by_province = json.loads(open('TestSv\Sv\cronjob\placeid_by_province.json', 'r', encoding='utf-8').read())

# define url constants
hotel_amenities = ['Spa', 'Hồ bơi', 'Gần biển', 'Free-Wifi', 'Bãi đỗ xe', 'Thang máy', 'Giặt ủi', 'Thuê xe máy', 'Phòng gia đình'] # mock data
geoapify_url = 'https://api.geoapify.com/v2/places?categories=accommodation&filter=place:{}&limit=500&apiKey={}'
detail_url = 'https://api.opentripmap.com/0.1/en/places/xid/{}?apikey={}'

# mkdir
current_time = datetime.datetime.now().strftime('%Y%m%d')
directory = 'crawl_pois/'+current_time
if not os.path.exists(directory):
    os.makedirs(directory)
f = open(directory+'/crawl_hotels.json', 'w', encoding='utf-8')

open_provinces = [{'province_id': ProvinceEnum[province].value.code, 'name': ProvinceEnum[province].value.name} for province in ProvinceEnum.__members__]

list_hotels = []
xids = [hotel['xid'] for hotel in list(recommender.vn_hotels_2.find())]

try:
    for provinces in list_placeid_by_province:
        province_name, place_id = list(provinces.items())[0]
        geoapify_url_ = geoapify_url.format(place_id, GEOAPIFY_APIKEY)
        list_response = requests.get(geoapify_url_).json()
        features = list_response['features']
        for item in features:
            properties = item['properties']
            hotel = {}
            if 'name' in properties and properties['name'] is not None and properties['name'] != '':
                # check if xid existed?
                data_source_raw = properties['datasource']['raw']
                osm_id = str(data_source_raw['osm_id'])
                osm_type = str(data_source_raw['osm_type'])
                xid = osm_type.upper()+osm_id
                if xid in xids:
                    continue

                detail_url_ = detail_url.format(xid, OPENTRIPMAP_APIKEY)
                detail_reponse = requests.get(detail_url_).json()
                if 'error' in detail_reponse:
                    continue

                if data_source_raw['tourism'] != 'hotel':
                    continue
                else: hotel['kinds'] = 'other_hotels'

                if 'phone' not in data_source_raw and 'email' not in data_source_raw:
                    continue

                # create data 
                hotel['xid'] = xid
                hotel['province_name'] = province_name
                hotel['name'] = properties['name']
                hotel['lat'] = properties['lat']
                hotel['lon'] = properties['lon']
                hotel['amenities'] = ','.join(sample(hotel_amenities,randint(5, 9))) # mock data
                hotel['rate'] = detail_reponse['rate']
                hotel['kinds'] = detail_reponse['kinds']
                hotel['province_id'] = find_ele_in_list_obj_by_prop(open_provinces, 'name', province_name)[0]['province_id']

                if 'phone' in data_source_raw:
                    hotel['phone'] = str(data_source_raw['phone'])
                if 'email' in data_source_raw:
                    hotel['email'] = str(data_source_raw['email'])
                else:
                    hotel['email'] = ''

                hotel['address'] = properties['formatted']
                
                list_hotels.append(hotel)

except Exception as ex:
    print(traceback.format_exc())

f.write(json.dumps(list_hotels))
f.close()
print('total time: ', str(time.time()-start))
# it often takes about 6721seconds ~ 1.86hours and >500 documents if not check exist else >10 documents

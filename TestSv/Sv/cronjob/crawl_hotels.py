# import
import json
from random import randint, sample
import requests
import datetime
import regex
import os
import time

from dotenv import load_dotenv
from pymongo import MongoClient

start = time.time()
print('started...')

# init
client = MongoClient()
recommender = client.recommender

# load env
load_dotenv()
GEOAPIFY_APIKEY = os.getenv('GEOAPIFY_APIKEY')

# reading file
list_placeid_by_province = json.loads(open('TestSv\Sv\cronjob\placeid_by_province.json', 'r', encoding='utf-8').read())

# define url constants
hotel_amenities = ['Spa', 'Hồ bơi', 'Gần biển', 'Free-Wifi', 'Bãi đỗ xe', 'Thang máy', 'Giặt ủi', 'Thuê xe máy', 'Phòng gia đình']
geoapify_url = 'https://api.geoapify.com/v2/places?categories=accommodation&filter=place:{}&limit=500&apiKey={}'

# mkdir
current_time = datetime.datetime.now().strftime('%Y%m%d')
directory = 'crawl_pois/'+current_time
if not os.path.exists(directory):
    os.makedirs(directory)
f = open(directory+'/crawl_hotels.json', 'w', encoding='utf-8')

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
                if osm_type.upper()+osm_id in xids:
                    continue
                
                # create data 
                hotel['xid'] = osm_type.upper()+osm_id 
                hotel['province_name'] = province_name
                hotel['name'] = properties['name']
                hotel['lat'] = properties['lat']
                hotel['lon'] = properties['lon']
                hotel['amenities'] = ','.join(sample(hotel_amenities,randint(5, 9))) # mock data

                if data_source_raw['tourism'] != 'hotel':
                    continue
                else: hotel['kinds'] = 'other_hotels'

                if 'phone' not in data_source_raw and 'email' not in data_source_raw:
                    continue

                if 'phone' in data_source_raw:
                    hotel['phone'] = str(data_source_raw['phone'])
                if 'email' in data_source_raw:
                    hotel['email'] = str(data_source_raw['email'])
                else:
                    hotel['email'] = ''

                list_hotels.append(hotel)

except Exception as ex:
    print(ex)

f.write(json.dumps(list_hotels))
f.close()
print('total time: ', str(time.time()-start))
# it often takes about 120seconds ~ 2minute and >500 documents if not check exist else >10 documents

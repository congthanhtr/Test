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

list_placeid_by_province = json.loads(open('TestSv\Sv\cronjob\placeid_by_province.json', 'r', encoding='utf-8').read())

# define url constants
geoapify_url = 'https://api.geoapify.com/v2/places?categories=catering.restaurant&filter=place:{}&limit=500&apiKey={}'
restaurant_amenities = ['Rộng rãi', 'Sạch sẽ', 'Đồ ăn ngon', 'Phục vụ tốt', 'Bãi đỗ xe', 'Gần trung tâm', 'Có sân khấu', 'Thực đơn đa dạng', 'Phòng VIP', 'Tổ chức tiệc']

# get list provinces in Vietnam
current_time = datetime.datetime.now().strftime('%Y%m%d')
directory = 'crawl_pois/'+current_time
if not os.path.exists(directory):
    os.makedirs(directory)
f = open(directory+'/crawl_restaurants.json', 'w', encoding='utf-8')
list_restaurants = []
xids = [restaurant['xid'] for restaurant in list(recommender.vn_restaurants.find())]
try:
    for provinces in list_placeid_by_province:
        province_name, place_id = list(provinces.items())[0]
        geoapify_url_ = geoapify_url.format(place_id, GEOAPIFY_APIKEY)
        list_response = requests.get(geoapify_url_).json()
        features = list_response['features']
        for item in features:
            properties = item['properties']
            restaurant = {}
            if 'name' in properties and properties['name'] is not None and properties['name'] != '':
                # check if xid existed?
                data_source_raw = properties['datasource']['raw']
                osm_id = str(data_source_raw['osm_id'])
                osm_type = str(data_source_raw['osm_type'])
                if osm_type.upper()+osm_id in xids:
                    continue
                
                # create data 
                restaurant['xid'] = osm_type.upper()+osm_id
                restaurant['province_name'] = province_name
                restaurant['name'] = properties['name']
                restaurant['lat'] = properties['lat']
                restaurant['lon'] = properties['lon']
                restaurant['kinds'] = 'restaurants'
                restaurant['amenities'] = ','.join(sample(restaurant_amenities,randint(5, 10)))

                if 'phone' not in data_source_raw and 'email' not in data_source_raw:
                    continue

                if 'phone' in data_source_raw:
                    restaurant['phone'] = str(data_source_raw['phone'])
                if 'email' in data_source_raw:
                    restaurant['email'] = str(data_source_raw['email'])
                else:
                    restaurant['email'] = ''

                list_restaurants.append(restaurant)

except Exception as ex:
    print(ex)

f.write(json.dumps(list_restaurants))
f.close()
print('total time: ', str(time.time()-start))
# it often takes about 100seconds ~ 1minute30seconds and >800 documents

# import
import json
import requests
import datetime
import regex
import os
import time

from dotenv import load_dotenv
from deep_translator import GoogleTranslator 
from pymongo import MongoClient

start = time.time()
print('started...')
# init
client = MongoClient()
tranlator = GoogleTranslator(target='vi')
recommender = client.recommender

# load env
load_dotenv()
OPENTRIPMAP_APIKEY = os.getenv('OPENTRIPMAP_APIKEY')

# define url constants
list_url = 'https://api.opentripmap.com/0.1/en/places/bbox?limit=500&kinds={}&lon_min={}&lon_max={}&lat_min={}&lat_max={}&apikey={}'
detail_url = 'https://api.opentripmap.com/0.1/en/places/xid/{}?apikey={}'

# get list provinces in Vietnam
vn_provinces = list(recommender.vn_provinces.find({}))

# mkdir
current_time = datetime.datetime.now().strftime('%Y%m%d')
directory = 'crawl_pois/'+current_time
if not os.path.exists(directory):
    os.makedirs(directory)
f = open('/crawl_pois.json', 'w', encoding='utf-8')
list_pois = []
xids = [poi['xid'] for poi in list(recommender.vn_pois.find())]
try:
    for provinces in vn_provinces:
        boundary_box = provinces['boundary_box']
        kinds = 'interesting_places,resorts,sport,amusements' # get all kinds: https://opentripmap.io/catalog
        list_url_ = list_url.format(kinds, boundary_box[2], boundary_box[3], boundary_box[0], boundary_box[1], OPENTRIPMAP_APIKEY)
        list_response = requests.get(list_url_).json()
        '''
        list_response looks like:
        {
            "type": "FeatureCollection",
            "features": [
                "type": "Feature",
                "id": "......",
                "geometry": {
                    "type": "Point",
                    "coordinate": [
                        <lat>,
                        <lon>
                    ]
                },
                "properties": [
                    "xid": "......",
                    <main information>
                    ...
                ]
            ],
            ...
        }
        '''
        features = list_response['features']
        for item in features:
            properties = item['properties']
            poi = {}
            if 'name' in properties and properties['name'] is not None and properties['name'] != '':
                if properties['xid'] in xids:
                    continue
                detail_ = detail_url.format(properties['xid'], OPENTRIPMAP_APIKEY)
                detail_response = requests.get(detail_).json()
                '''
                detail_response in a best case will look like. Sometimes, data will not include all of these attributes
                {
                    "xid": "R7146562",
                    "name": "Tram Chim National Park",
                    "address": {
                        "state": "Tỉnh Đồng Tháp",
                        "county": "Tam Nông",
                        "country": "Việt Nam",
                        "country_code": "vn"
                    },
                    "rate": "3h",
                    "osm": "relation/7146562",
                    "bbox": {
                        "lon_min": 105.464897,
                        "lon_max": 105.607783,
                        "lat_min": 10.678079,
                        "lat_max": 10.758214
                    },
                    "wikidata": "Q586985",
                    "kinds": "urban_environment,gardens_and_parks,cultural,natural,interesting_places,nature_reserves,national_parks",
                    "voyage": "https://vi.wikivoyage.org/wiki/V%C6%B0%E1%BB%9Dn%20qu%E1%BB%91c%20gia%20Tr%C3%A0m%20Chim",
                    "sources": {
                        "geometry": "osm",
                        "attributes": [
                            "osm",
                            "wikidata"
                        ]
                    },
                    "otm": "https://opentripmap.com/en/card/R7146562",
                    "wikipedia": "https://en.wikipedia.org/wiki/Tr%C3%A0m%20Chim%20National%20Park",
                    "image": "https://commons.wikimedia.org/wiki/File:%C4%90%E1%BB%93ng_c%E1%BB%8F_v%C3%A0_chim_n%C6%B0%E1%BB%9Bc.jpg",
                    "preview": {
                        "source": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/%C4%90%E1%BB%93ng_c%E1%BB%8F_v%C3%A0_chim_n%C6%B0%E1%BB%9Bc.jpg/400px-%C4%90%E1%BB%93ng_c%E1%BB%8F_v%C3%A0_chim_n%C6%B0%E1%BB%9Bc.jpg",
                        "height": 266,
                        "width": 400
                    },
                    "wikipedia_extracts": {
                        "title": "en:Tràm Chim National Park",
                        "text": "Tràm Chim National Park (Vietnamese: Vườn quốc gia Tràm Chim) is a national park in the Plain of Reeds in the Mekong Delta region of Vietnam. The park was created to restore a degraded wetland, in order to protect several rare birds, especially the sarus crane (Grus antigone sharpii)--a species listed on the IUCN Red List. It is also a designated wetland of international importance under the Ramsar Convention.",
                        "html": "<p><b>Tràm Chim National Park</b> (Vietnamese: <i lang=\"vi\">Vườn quốc gia Tràm Chim</i>) is a national park in the Plain of Reeds in the Mekong Delta region of Vietnam. The park was created to restore a degraded wetland, in order to protect several rare birds, especially the sarus crane (<i>Grus</i> <i>antigone sharpii</i>)--a species listed on the IUCN Red List. It is also a designated wetland of international importance under the Ramsar Convention.</p>"
                    },
                    "point": {
                        "lon": 105.50010681152344,
                        "lat": 10.72989273071289
                    }
                }
                '''
                # check if request error
                if 'error' in detail_response:
                    continue
                
                # check province name of poi. sometimes Bắc Ninh's boundary box will get some Hà Nội's pois
                # so we dont neet to add them to db
                if 'address' not in detail_response:
                    continue
                address = detail_response['address']
                current_province_name = provinces['admin_name']
                if 'state' in address:
                    req_province_name = address['state']
                elif 'city' in address:
                    req_province_name = address['city']
                elif 'region' in address:
                    req_province_name = address['region']

                if current_province_name.replace('-', '').replace(' ','') not in req_province_name.replace('-','').replace(' ',''):
                    continue
                
                # next, preprocess data
                if regex.match('\d+m|viewpoint|bike|\'s|ty|ngoại|free|home|\/|công|đình|cong|cty|ty|hike|min|trail|360|view|^\d(?i)', properties['name']):
                    if properties['rate'] == 1:
                        print(properties['name'])
                        continue

                # create data 
                poi['province_name'] = provinces['admin_name']
                poi['province_id'] = provinces['place_id']
                poi['xid'] = properties['xid']
                poi['name'] = properties['name']
                try:
                    poi['vi_name'] = tranlator.translate(poi['name'])
                except:
                    poi['vi_name'] = poi['name']

                poi['rate'] = properties['rate']
                poi['kinds'] = properties['kinds']

                if 'preview' in detail_response:
                    poi['preview'] = detail_response['preview']
                else:
                    poi['preview'] = None
                
                if 'wikipedia_extracts' in detail_response:
                    poi['description'] = detail_response['wikipedia_extracts']['text']
                    try:
                        poi['vi_description'] = tranlator.translate(poi['description'])
                    except:
                        poi['vi_description'] = poi['description']
                else:
                    poi['description'] = None
                    poi['vi_description'] = None

                if 'point' in detail_response:
                    poi['point'] = detail_response['point']
                else:
                    poi['point'] = None

                list_pois.append(poi)

except Exception as ex:
    print(str(ex))

f.write(json.dumps(list_pois))
f.close()
print('total time: ', str(time.time()-start))
# take about 17500seconds ~ 4.8hours and >6000 documents if not check exist

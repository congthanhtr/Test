from datetime import datetime
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import time
import json
from dateutil import parser

from django.conf import settings

print(settings.SECRET_KEY)

# load env
start=time.time()
load_dotenv()
DOMAIN_NAME = os.getenv('DOMAIN_NAME')
SECRET_KEY = os.getenv('SECRET_KEY')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')
headers = {'Authorization': SECRET_KEY}

print('connecting to db...')
client = MongoClient()
print('connected to database...')

log_tour_created = client.recommender.log_tour_created
log_tour_created_today = list(log_tour_created.find({'log_created_date': {'$gte': datetime(2023, 5, 1), '$ne': None}}, {'_id': 0, 'ref': 0, 'log_created_date': 0}))
print(len(log_tour_created_today))

# for log in log_tour_created_today:
#     req = requests.post(DOMAIN_NAME+'api/v2/extract_info_to_excel', headers=headers, data=json.dumps(log)).json()

print(time.time()-start)
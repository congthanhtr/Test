from ..service.time_travel import TimeTravelService
import pandas as pd
import joblib
from pymongo import MongoClient
from sklearn import metrics
from sklearn import tree

from django.conf import settings

CONNECTION_STRING = settings.CONNECTION_STRING


client = MongoClient(CONNECTION_STRING)
db = client.recommender

collection_driving_time = db.get_collection('vn_provinces_driving_time')
collection_provinces = db.get_collection('vn_provines')
collection_provinces_has_train = db.get_collection('vn_provinces').find({
    'has_train': True
}, {
    'admin_name': 1,
    '_id': 0
})

list_provinces_has_train = []
for i in collection_provinces_has_train:
    list_provinces_has_train.append(i['admin_name'])


# read train data
df = pd.read_excel("static/predict_transport.xlsx")
x_train = df.drop("transport", axis="columns")
y_train = df['transport']
city_from = df['from']
city_to = df['to']

distance = []
driving_time = []
railway_time = []
flight_time = []

service = TimeTravelService()
for i in range(0, len(city_from)):
    mcollection = db.get_collection('vn_provinces_driving_time').find({'from': city_from[i], 'to': city_to[i]})
    
    for driving in mcollection:
        distance.append(driving['distance'])
        driving_time.append(driving['driving_time'])
    if city_from[i] in list_provinces_has_train and city_to[i] in list_provinces_has_train:
        railway_time.append(driving['distance']/50.0*60)
    else:
        railway_time.append(0)

    time_travel = service.calculate_time_travel([city_from[i]], [city_to[i]])
    flight_time.append(time_travel.flight_time)


x_train['distance'] = distance
x_train['driving_time'] = driving_time
x_train['flight_time'] = flight_time
x_train['railway_time'] = railway_time
x_train = x_train.drop(columns=['from', 'to', 'ref'])

# read test data
df_test = pd.read_excel("static/predict_transport_test.xlsx")
x_test = df_test.drop("transport", axis="columns")
y_test = df_test["transport"]
city_from_test = df_test['from']
city_to_test = df_test['to']

distance_test = []
driving_time_test = []
railway_time_test = []
flight_time_test = []

for i in range(0, len(city_from_test)):
    mcollection = db.get_collection('vn_provinces_driving_time').find({'from': city_from_test[i], 'to': city_to_test[i]})
    
    for driving in mcollection:
        distance_test.append(driving['distance'])
        driving_time_test.append(driving['driving_time'])
    if city_from_test[i] in list_provinces_has_train and city_to_test[i] in list_provinces_has_train:
        railway_time_test.append(driving['distance']/50.0*60)
    else:
        railway_time_test.append(0)

    time_travel = service.calculate_time_travel([city_from_test[i]], [city_to_test[i]])
    flight_time_test.append(time_travel.flight_time)

x_test['distance'] = distance_test
x_test['driving_time'] = driving_time_test
x_test['flight_time'] = flight_time_test
x_test['railway_time'] = railway_time_test
x_test = x_test.drop(columns=['from', 'to', 'ref'])

model = tree.DecisionTreeClassifier()
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
print("Accuracy: ", metrics.accuracy_score(y_test, y_pred))

# with open("./Sv/ml_model/result/predict_transport.pkl", "wb") as f:
#     joblib.dump(model, f)

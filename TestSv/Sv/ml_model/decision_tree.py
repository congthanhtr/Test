import pickle
# import pandas as pd
# from sklearn.preprocessing import LabelEncoder
# from sklearn import tree

# df = pd.read_excel("static/training_data.xlsx")
# inputs = df.drop("ShouldPlane", axis="columns")
# pred_Y = df['ShouldPlane']


# label_days = LabelEncoder()
# label_nights = LabelEncoder()
# label_tourTypes = LabelEncoder()

# inputs['distance_n'] = inputs['Distance(km)']
# inputs['planeTime_n'] = inputs['planeTime(m)']
# inputs['busTime_n'] = inputs['busTime(m)']
# inputs['days_n']= label_days.fit_transform(inputs['Days'])
# inputs['nights_n']= label_nights.fit_transform(inputs['Nights'])
# inputs['tourType_n']= label_tourTypes.fit_transform(inputs['TourType'])

# pred_X = inputs.drop(['Distance(km)',"planeTime(m)",'busTime(m)','Days','Nights','TourType'],axis="columns")

# model = tree.DecisionTreeClassifier()
# model.fit(pred_X.values,pred_Y.values)
# # with open("./Sv/ml_model/result/predict_vihicles.pkl", "wb") as f:
# #     pickle.dump(model, f)
# # model.score(pred_X,pred_Y)
# # data_pred = model.predict([[20,2,1,1,0]]) 

from ..service.time_travel import TimeTravelService

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn import tree
import joblib
from pymongo import MongoClient

client = MongoClient()
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

df = pd.read_excel("static/predict_transport.xlsx")
inputs = df.drop("transport", axis="columns")
pred_Y = df['transport']
city_from = df['from']
city_to = df['to']

distance = []
driving_time = []
railway_time = []
flight_time = []

service = TimeTravelService()
for i in range(0, len(city_from)):
    # for driving in collection_driving_time.find({
    #     'from': city_from[i],
    #     'to': city_to[i]
    # }):
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


inputs['distance'] = distance
inputs['driving_time'] = driving_time
inputs['flight_time'] = flight_time
inputs['railway_time'] = railway_time

inputs = inputs.drop(columns=['from', 'to', 'ref'])

print(inputs)
model = tree.DecisionTreeClassifier()
model.fit(inputs.values, pred_Y.values)

with open("./Sv/ml_model/result/predict_transport.pkl", "wb") as f:
    joblib.dump(model, f)

# pred_X = inputs.drop(['Distance(km)',"planeTime(m)",'busTime(m)','Days','Nights','TourType'],axis="columns")

# model = tree.DecisionTreeClassifier()
# model.fit(pred_X.values,pred_Y.values)
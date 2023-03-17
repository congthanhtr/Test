import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn import tree

df = pd.read_excel("static/training_data.xlsx")
inputs = df.drop("ShouldPlane", axis="columns")
pred_Y = df['ShouldPlane']


label_days = LabelEncoder()
label_nights = LabelEncoder()
label_tourTypes = LabelEncoder()

inputs['distance_n'] = inputs['Distance(km)']
inputs['planeTime_n'] = inputs['planeTime(m)']
inputs['busTime_n'] = inputs['busTime(m)']
inputs['days_n']= label_days.fit_transform(inputs['Days'])
inputs['nights_n']= label_nights.fit_transform(inputs['Nights'])
inputs['tourType_n']= label_tourTypes.fit_transform(inputs['TourType'])

pred_X = inputs.drop(['Distance(km)',"planeTime(m)",'busTime(m)','Days','Nights','TourType'],axis="columns")

model = tree.DecisionTreeClassifier()
model.fit(pred_X.values,pred_Y.values)
# with open("./Sv/ml_model/result/predict_vihicles.pkl", "wb") as f:
#     pickle.dump(model, f)
# model.score(pred_X,pred_Y)
# data_pred = model.predict([[20,2,1,1,0]]) 
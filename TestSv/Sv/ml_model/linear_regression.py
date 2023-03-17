import pickle
import pandas as pd
from sklearn import linear_model

df = pd.read_excel("static/linear_data.xlsx")

x_train = df.drop("Places", axis="columns")

y_train = df.Places

lm_model = linear_model.LinearRegression()
lm_model.fit(x_train.values,y_train.values)
# with open("./Sv/ml_model/result/predict_n_places.pkl", "wb") as f:
#     pickle.dump(lm_model, f)
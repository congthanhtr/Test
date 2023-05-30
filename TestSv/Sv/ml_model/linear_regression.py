import pickle
import pandas as pd
from sklearn import linear_model

# df = pd.read_excel("static/linear_data.xlsx")

# x_train = df.drop("Places", axis="columns")

# y_train = df.Places

# lm_model = linear_model.LinearRegression()
# lm_model.fit(x_train.values,y_train.values)
# with open("./Sv/ml_model/result/predict_n_places.pkl", "wb") as f:
#     pickle.dump(lm_model, f)

class LinearRegressionModel:

    data_path = 'static/linear_data_.xlsx'
    result_path = './Sv/ml_model/result/predict_n_places_.pkl'

    def train_model(self, new_data):
        df = pd.DataFrame(new_data)
        if new_data is not None:
            with pd.ExcelFile(self.data_path,mode='a',engine='openpyxl',if_sheet_exists='overlay') as writer:
                df.to_excel(writer,sheet_name='Sheet1',header=None,startrow=writer.sheets['Sheet1'].max_row,index=False)
            
            new_df = pd.read_excel(self.data_path)
            x_train = new_df.drop("Places", axis="columns")
            y_train = new_df.Places
            # new retrain model
            lm_model = linear_model.LinearRegression()
            lm_model.fit(x_train.values,y_train.values)
            with open(self.result_path, "wb") as f:
                pickle.dump(lm_model, f)  

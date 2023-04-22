import joblib as pickle
# import pickle
from django.core.cache import cache


class MachineLearningModel:
    _model = None

    def __init__(self, model) -> None:
        self._model = model

    def predict(self, data):
        return self._model.predict(data)

class MachineLearningService:
    model_path: str = ''
    model: MachineLearningModel = None


    PREDICT_N_PLACES_PATH = './Sv/ml_model/result/predict_n_places.pkl'
    PREDICT_VIHICLES_PATH = './Sv/ml_model/result/predict_vihicles.pkl'
    PREDICT_TRANSPORT_PATH = './Sv/ml_model/result/predict_transport.pkl'

    def load_model(self, model_path, model_name):
        model = cache.get(model_name)
        if model is not None:
            return model
        self.model_path = model_path
        f = open(self.model_path, 'rb')
        ml_model = pickle.load(f)
        f.close()
        self.model = MachineLearningModel(ml_model)
        cache.set(model_name, self)
        return self

    def get_predict_n_places_model(self):
        return self.load_model(self.PREDICT_N_PLACES_PATH,'predict_n_places')

    def get_predict_vihicles_model(self):
        return self.load_model(self.PREDICT_VIHICLES_PATH, 'predict_vihicles')

    def get_predict_transport_model(self):
        return self.load_model(self.PREDICT_TRANSPORT_PATH, 'predict_transport')

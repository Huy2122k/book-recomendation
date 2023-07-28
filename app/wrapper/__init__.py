import json
import random

from data_manager.DataManager import DataManager
from flask import request

with open("credentials.json", "r") as f:
    credentials = json.load(f)

class AppWrapper(object):
    
    def __init__(self, app, **configs):
        self.app = app
        self.configs(**configs)

    def configs(self, **configs):
        for config, value in configs:
            self.app.config[config.upper()] = value

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET'], *args, **kwargs):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods, *args, **kwargs)

    def run(self, **kwargs):
        self.app.run(**kwargs)

    def init_recommendations(self, SUPPORT_RECOMMENDATIONS_CLASS):
        self.data_manager = DataManager()
        self.SUPPORT_RECOMMENDATIONS_CLASS = SUPPORT_RECOMMENDATIONS_CLASS
        for rec_cls in SUPPORT_RECOMMENDATIONS_CLASS:
            name = rec_cls.__name__.lower()
            print(name)
            setattr(self, name, rec_cls())

    def recommend(self, id, type):
        num_rec = request.args.get('num_rec', 5)
        return getattr(self, type).predict(id, num_rec)
    
    def get_samples(self):
        data = []
        for rec_cls in self.SUPPORT_RECOMMENDATIONS_CLASS:
            name = rec_cls.__name__.lower()
            data += [getattr(self, name).samples()]
        return data

    def get_popular_books(self):
        return random.choices(self.data_manager.get_popular_books(30), k=10)

    def summary_recommend(self, id, type):
        num_rec = request.args.get('num_rec', 5)
        return getattr(self, type).predict(id, num_rec)
    
    def update_rec_models(self):
        for rec_model in self.SUPPORT_RECOMMENDATIONS_CLASS:
            rec_model.save_model()

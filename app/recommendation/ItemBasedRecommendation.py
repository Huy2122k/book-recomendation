import os
import pathlib
import pickle
from datetime import datetime, timedelta

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from data_manager import DataManager
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize

from .Recommendation import Recommendation


class ItemBasedRecommendation(Recommendation):
    
    def __init__(self, base_number=5, *args):
        super().__init__(*args)
        self.model = None
        self.base_number = base_number
        self.cache_time = datetime.now()
        self.get_model()

    @classmethod
    def save_model(cls, min_rating_count=100, k_neighbors=5):
        data_manager = DataManager()
        rating = data_manager.get_data_from_db("rating")
        # Drop users who vote less than min_rating_count times.
        rating = rating[rating["Rating"] > 0]
        book_rating_count = rating[rating['BookID'].map(rating['BookID'].value_counts()) < min_rating_count]['BookID'].values
        user_rating_count = rating[rating['AccountID'].map(rating['AccountID'].value_counts()) < 50]['AccountID'].values
        df = rating[~rating['BookID'].isin(book_rating_count)] 
        df = df[~df['AccountID'].isin(user_rating_count)] 
        # Tạo mapping giữa tên người dùng và chỉ mục trong ma trận đánh giá
        user_index_mapping = {user: i for i, user in enumerate(df['AccountID'].unique())}
        book_index_mapping = {item: i for i, item in enumerate(df['BookID'].unique())}
        # Xây dựng ma trận đánh giá dưới dạng ma trận thưa (sparse matrix)
        num_users = df['AccountID'].nunique()
        num_items = df['BookID'].nunique()
        book_user_matrix = np.zeros((num_items, num_users))
        for _, row in df.iterrows():
            user_idx = user_index_mapping[row['AccountID']]
            item_idx = book_index_mapping[row['BookID']]
            book_user_matrix[item_idx, user_idx] = row['Rating']
        # normalize
        book_user_matrix = normalize(book_user_matrix, norm='l2', axis=1)
        knn_model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=k_neighbors)
        knn_model.fit(book_user_matrix)

        model = {
            "knn_model": knn_model,
            "user_index_mapping": user_index_mapping,
            "book_index_mapping" :book_index_mapping,
            "book_user_matrix": book_user_matrix
        }
        with open(f'models/{cls.__name__}/model.pkl', 'wb') as f:
            pickle.dump(model, f)

    def get_model(self):
        if self.model is None or self.cache_time + timedelta(hours = 12) > datetime.now():
            self.load_model()
            self.cache_time =  datetime.now()
        return self.model
    
    def load_model(self):
        if not os.path.exists(f"models/{self.__class__.__name__}/model.pkl"):
            self.__class__.save_model()
        with open(f"models/{self.__class__.__name__}/model.pkl", "rb") as f:
            model = pickle.load(f)
        self.model = model

    def item_based(self, book_id, rec_number):
        model = self.model
        knn_model = model['knn_model']
        book_index_mapping = model['book_index_mapping']
        book_user_matrix = model['book_user_matrix']
        index_book_mapping = {i: item for item, i in book_index_mapping.items()}

        if book_id in book_index_mapping.keys():
            # find nearest neighbors
            _, neighbor_indices = knn_model.kneighbors([book_user_matrix[book_index_mapping[book_id]]], n_neighbors=rec_number+1)
            # remove itself from recommendations list
            neighbor_indices = neighbor_indices.squeeze()[1:]
            recommended_items = [index_book_mapping[neighbor_index] for neighbor_index in neighbor_indices]
            return recommended_items
        else:
            return []

    def predict(self, book_id, rec_number):
        book_rec_ids = self.item_based(book_id, rec_number)
        return book_rec_ids
    
    def samples(self):
        return {
            "name": self.__class__.__name__.lower(),
            "sample_book_ids":  list(self.model['book_index_mapping'].keys())[:10],
            "cache": self.cache_time,
            "update_at": datetime.fromtimestamp(pathlib.Path(f"models/{self.__class__.__name__}/model.pkl").stat().st_mtime)
        }

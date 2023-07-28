import os
import pathlib
import pickle
from datetime import datetime, timedelta

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from data_manager import DataManager
from sklearn.metrics.pairwise import cosine_similarity

from .Recommendation import Recommendation


def get_max_top_n_indices(arr, n=5, exclude_indices = []):
    sorted_indices = np.argsort(arr)[::-1]
    sorted_indices = [ index for index in sorted_indices if index not in set(exclude_indices)]
    sorted_indices = sorted_indices[:n]
    return sorted_indices

class UserBasedRecommendation(Recommendation):
    def __init__(self, base_number=5, *args):
        super().__init__(*args)
        self.model = None
        self.base_number = base_number
        self.cache_time = datetime.now()
        self.get_model()

    @classmethod
    def save_model(cls, min_rating_count=50):
        data_manager = DataManager()
        rating = data_manager.get_data_from_db("rating")
        df = rating[rating['AccountID'].map(rating['AccountID'].value_counts()) > min_rating_count]  # Drop users who vote less than min_rating_count times.
        # Tạo mapping giữa tên người dùng và chỉ mục trong ma trận đánh giá
        user_index_mapping = {user: i for i, user in enumerate(df['AccountID'].unique())}
        book_index_mapping = {item: i for i, item in enumerate(df['BookID'].unique())}
        user_rated = { user : set([]) for user in df['AccountID'].unique()}
        # Xây dựng ma trận đánh giá dưới dạng ma trận thưa (sparse matrix)
        num_users = df['AccountID'].nunique()
        num_items = df['BookID'].nunique()
        user_book_matrix = np.zeros((num_users, num_items))

        for _, row in df.iterrows():
            user_rated[row['AccountID']].add(row['BookID'])
            user_idx = user_index_mapping[row['AccountID']]
            item_idx = book_index_mapping[row['BookID']]
            user_book_matrix[user_idx, item_idx] = row['Rating']

        invalid_mask = (user_book_matrix == 0).all(axis=1)
        user_book_matrix[invalid_mask] = 0.01
        del invalid_mask
        user_book_matrix_norm = user_book_matrix / np.linalg.norm(user_book_matrix, axis=1, keepdims=True)

        user_similar = cosine_similarity(user_book_matrix_norm)

        # create model
        model = {}
        model["user_rated"] = user_rated
        model["user_index_mapping"] = user_index_mapping
        model["book_index_mapping"] = book_index_mapping
        model["user_similar"] = user_similar

        if not os.path.exists(f"models/{cls.__name__}"):
            # Create the directory if it doesn't exist
            os.makedirs(f"models/{cls.__name__}")
        # save model
        with open(f"models/{cls.__name__}/model.pkl", "wb") as f:
            pickle.dump(model, f)
            # save rating
        rating.to_csv(f"models/{cls.__name__}/rating.csv")

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
        self.rating = pd.read_csv(f"models/{self.__class__.__name__}/rating.csv", low_memory=True, memory_map=True)
        self.model = model

    def user_based(self, id, rec_number=5):
        model = self.model
        rating = self.rating
        if id not in self.model['user_rated'].keys():
            print("User NOT FOUND ")
            return {"similar_users": [], "similar_books": []}
        else:
            user_similar = model['user_similar']
            user_rated = model['user_rated']
            user_index_mapping = model['user_index_mapping']
            book_index_mapping = model['book_index_mapping']
            index_user_mapping = {index: user for user, index in user_index_mapping.items()}

            account_index = user_index_mapping[id]

            # get similar users and remove itself
            similar_users = get_max_top_n_indices(user_similar[account_index], self.base_number, [account_index])
            similar_users = [index_user_mapping[index] for index in  similar_users]

            recommend_books = []
            for user in similar_users:
                recommend_books += rating[(
                    rating['AccountID'] == user
                    ) & (
                    ~rating['BookID'].isin(user_rated[id])
                )].sort_values(by=['Rating'], ascending=False).BookID.values.tolist()[:rec_number]

            return {"similar_users": similar_users, "similar_books": recommend_books}

    def predict(self, user_id, rec_number=5):
        return self.user_based(user_id, rec_number)

    def samples(self):
        return {
            "name": self.__class__.__name__.lower(),
            "sample_user_ids":  list(self.model['user_index_mapping'].keys())[:10],
            "cache": self.cache_time,
            "update_at": datetime.fromtimestamp(pathlib.Path(f"models/{self.__class__.__name__}/model.pkl").stat().st_mtime)
        }

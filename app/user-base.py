import pickle

import numpy as np
import pandas as pd
import tqdm
from sklearn.metrics.pairwise import cosine_similarity

rating = pd.read_csv("models/UserBasedRecommendation/rating.csv", low_memory=True, memory_map=True)
df = rating
df = rating[rating['AccountID'].map(rating['AccountID'].value_counts()) > 50]  # Drop users who vote less than min_rating_count times.
# Tạo mapping giữa tên người dùng và chỉ mục trong ma trận đánh giá
user_index_mapping = {user: i for i, user in enumerate(df['AccountID'].unique())}
book_index_mapping = {item: i for i, item in enumerate(df['BookID'].unique())}
user_rated = { user : set([]) for user in df['AccountID'].unique()}
# Xây dựng ma trận đánh giá dưới dạng ma trận thưa (sparse matrix)
num_users = df['AccountID'].nunique()
num_items = df['BookID'].nunique()
user_book_matrix = np.zeros((num_users, num_items))
for _, row in tqdm.tqdm(df.iterrows()):
    user_rated[row['AccountID']].add(row['BookID'])
    user_idx = user_index_mapping[row['AccountID']]
    item_idx = book_index_mapping[row['BookID']]
    user_book_matrix[user_idx, item_idx] = row['Rating']

invalid_mask = (user_book_matrix == 0).all(axis=1)
user_book_matrix[invalid_mask] = 0.01
del invalid_mask
user_book_matrix_norm = user_book_matrix / np.linalg.norm(user_book_matrix, axis=1, keepdims=True)

user_similar = cosine_similarity(user_book_matrix_norm)

model = {}
model["user_rated"] = user_rated
model["user_index_mapping"] = user_index_mapping
model["book_index_mapping"] = book_index_mapping
model["user_similar"] = user_similar

with open("models/UserBasedRecommendation/model.pkl", "wb") as f:
    pickle.dump(model, f)

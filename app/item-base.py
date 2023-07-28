import pickle

import numpy as np
import pandas as pd
import tqdm
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize

k_neighbors = 5
rating = pd.read_csv("models/rating.csv", low_memory=True, memory_map=True)

# Drop users who vote less than min_rating_count times.
rating = rating[rating["Rating"] > 0]
book_rating_count = rating[rating['BookID'].map(rating['BookID'].value_counts()) < 100]['BookID'].values
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
for _, row in tqdm.tqdm(df.iterrows()):
    user_idx = user_index_mapping[row['AccountID']]
    item_idx = book_index_mapping[row['BookID']]
    book_user_matrix[item_idx, user_idx] = row['Rating']

book_user_matrix = normalize(book_user_matrix, norm='l2', axis=1)

knn_model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=k_neighbors)
knn_model.fit(book_user_matrix)

model = {
    "knn_model": knn_model,
    "user_index_mapping": user_index_mapping,
    "book_index_mapping" :book_index_mapping,
    "book_user_matrix": book_user_matrix
}
with open('models/ItemBasedRecommendation/model.pkl', 'wb') as f:
    pickle.dump(model, f)

index_book_mapping = {i: item for item, i in book_index_mapping.items()}

_, neighbor_indices = knn_model.kneighbors([book_user_matrix[2]], n_neighbors=k_neighbors+1)
neighbor_indices = neighbor_indices.squeeze()[1:]
recommended_items = [index_book_mapping[neighbor_index] for neighbor_index in neighbor_indices]

with open('models/ItemBasedRecommendation/model.pkl', 'rb') as f:
    print(f.stat())

def load_knn_model(file_path):
    # Load mô hình KNN từ file bằng pickle
    with open(file_path, 'rb') as f:
        knn_model = pickle.load(f)
    return knn_model

# Ví dụ sử dụng
# ratings_matrix là ma trận đánh giá, mỗi hàng là một người dùng và mỗi cột là một sản phẩm
ratings_matrix = np.array([[3, 4, 0, 5],
                           [1, 2, 4, 3],
                           [5, 3, 2, 0],
                           [0, 5, 3, 2]])

target_item_index = 2  # Sản phẩm cần được gợi ý
num_recommendations = 2  # Số lượng sản phẩm được gợi ý
k_neighbors = 2  # Số lượng láng giềng trong KNN

# Kiểm tra xem mô hình đã tồn tại hay chưa
try:
    knn_model = load_knn_model('knn_model.pkl')
except FileNotFoundError:
    knn_model = None

if knn_model is None:
    # Nếu mô hình chưa tồn tại, huấn luyện mô hình và lưu vào file
    knn_model = item_based_recommendations_knn(ratings_matrix, target_item_index, num_recommendations, k_neighbors)
else:
    print("Mô hình KNN đã tồn tại, sử dụng lại mô hình.")

# Gợi ý các sản phẩm dựa trên mô hình KNN đã huấn luyện
recommended_items = item_based_recommendations_knn(ratings_matrix, target_item_index, num_recommendations, k_neighbors)
print("Các sản phẩm được gợi ý cho sản phẩm {}: {}".format(target_item_index, recommended_items))

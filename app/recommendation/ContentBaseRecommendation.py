from datetime import datetime, timedelta
from random import shuffle

import numpy as np  # linear algebra
from data_manager import DataManager
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .Recommendation import Recommendation


class ContentBaseRecommendation(Recommendation):
    
    def __init__(self, min_rating_count=10, *args):
        super().__init__(*args)
        self.model = None
        self.data_manager = DataManager()
        self.min_rating_count = min_rating_count
        self.cache_time = datetime.now()
        self.get_model()

    def process_data(self, books):
        book_index_map = { book_id: index for index, book_id in enumerate(books["BookID"].values)}
        index_book_mapping = {i: item for item, i in book_index_map.items()}

        titles = books["BookName"].values
        authors = books["Author"].values
        publishers = books["Publisher"].values
        # Tạo mã hóa vector cho tiêu đề, tác giả và nhà xuất bản
        vectorizer = CountVectorizer()
        title_vectors = vectorizer.fit_transform(titles).toarray()
        author_vectors = vectorizer.fit_transform(authors).toarray()
        publisher_vectors = vectorizer.fit_transform(publishers).toarray()
        return {
            "title_vectors": title_vectors,
            "author_vectors": author_vectors,
            "publisher_vectors": publisher_vectors,
            "book_index_map": book_index_map,
            "index_book_mapping": index_book_mapping
        }

    def get_model(self):
        if self.model is None or self.cache_time + timedelta(hours = 12) > datetime.now():
            books = self.data_manager.get_books_by_rating_count(self.min_rating_count, ["BookID","BookName","Author","Publisher"])
            books = books.sort_values(by=["CountRating"])
            self.cache_time = datetime.now() 
            self.model = self.process_data(books)
        return self.model

    def content_based(self, book_id, top_n):

        if book_id in self.model['book_index_map']:
            book_index = self.model['book_index_map'][book_id]
            index_book_mapping = self.model["index_book_mapping"]

            # get saved vectors
            title_vectors = self.model["title_vectors"]
            author_vectors = self.model["author_vectors"]
            publisher_vectors = self.model["publisher_vectors"]

            # get features vectors
            query_title_vector = title_vectors[book_index].reshape(1, -1)
            query_author_vector = author_vectors[book_index].reshape(1, -1)
            query_publisher_vector = publisher_vectors[book_index].reshape(1, -1)

            # Tính cosine similarity với các cuốn sách khác
            title_similarity = cosine_similarity(query_title_vector, title_vectors)[0]
            author_similarity = cosine_similarity(query_author_vector, author_vectors)[0]
            publisher_similarity = cosine_similarity(query_publisher_vector, publisher_vectors)[0]

            # Tổng hợp điểm số dựa trên tiêu đề, tác giả và nhà xuất bản
            total_similarity = 0.6*title_similarity + 0.3*author_similarity + 0.1*publisher_similarity

            # Sắp xếp và lấy top n sách gợi ý
            similar_books_indices = np.argsort(total_similarity)[::-1][1:top_n + 1]  # Bỏ qua sách cần tìm
            recommended_books = [index_book_mapping[i] for i in similar_books_indices]

            return recommended_books

        else:
            return []
    
    def predict(self, book_id, rec_number):
        book_rec_ids = self.content_based(book_id, rec_number)
        shuffle(book_rec_ids)
        return book_rec_ids
    
    def samples(self):
        return {
            "name": self.__class__.__name__.lower(),
            "sample_book_ids":  list(self.model['book_index_map'].keys())[:10],
            "min_rating_count": self.min_rating_count,
            "cache": self.cache_time,
            "update_at": self.cache_time
        }

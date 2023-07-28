



import os

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

class DataManager(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args):
        if hasattr(self, 'engine'):
            return
        # Lấy thông tin từ biến môi trường hoặc sử dụng giá trị mặc định nếu không có
        username = os.getenv("DB_USERNAME", "root")
        password = os.getenv("DB_PASSWORD", "1234")
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", 3306))

        self.engine = create_engine(f'mysql://{username}:{password}@{host}:{port}/library')
        
    def get_data_from_db(self, model, fields=[], size=None, limit=None, offset=None):
        field_str = ",".join(fields)if len(fields) > 0 else "*"
        sampling = ""
        if limit!= None and offset!=None:
            sampling = f"LIMIT {offset}, {limit}"
        
        if size is not None:
            sampling = f"LIMIT {size}"
        data = pd.read_sql(f'SELECT {field_str} FROM {model} {sampling}', self.engine) #read the entire table 
        return data

    def get_books_by_rating_count(self, min_rating_count, fields=[]):
        field_str = (",".join(fields) + ", r.CountRating")  if len(fields) > 0 else "*"
        data = pd.read_sql(
            f'SELECT {field_str} FROM book as b RIGHT JOIN (SELECT BookID as bid, COUNT(BookID) as CountRating FROM rating WHERE Rating > 0 GROUP BY BookID HAVING COUNT(BookID) > {min_rating_count}) as r ON b.BookID = r.bid ORDER BY r.CountRating DESC',
            self.engine
        ) #read the entire table 
        return data

    def get_top_most_rating(self, top_n=10):
        data = pd.read_sql(
            f'SELECT BookID FROM rating  WHERE Rating > 0 GROUP BY BookID ORDER BY SUM(rating) DESC LIMIT {top_n}',
            self.engine
        ) #read the entire table 
        return data["BookID"].values.tolist()
    
    def get_top_most_lending(self, top_n=10):
        data = pd.read_sql(
            f'SELECT bi.BookID FROM lendingbooklist as lbl LEFT JOIN bookitem as bi ON lbl.BookItemID = bi.BookItemID GROUP BY bi.BookID ORDER BY COUNT(bi.BookID) DESC LIMIT {top_n}',
            self.engine
        ) #read the entire table 
        return data["BookID"].values.tolist()


    def get_popular_books(self, top_n=10):
        return self.get_top_most_lending(int(top_n)) #+ self.get_top_most_rating(int(top_n/2)) + self.get_top_most_lending(int(top_n))

    def save_file(self, data, path):
        data.to_csv(path, index=False)

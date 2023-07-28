import datetime
import uuid

import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from tqdm import tqdm

engine = create_engine('mysql://root:1234@localhost/library')    

def seed_users():
    users = pd.read_csv("transformed/users.csv")
    batch_size = 5000
    for i in tqdm(range(0, len(users), batch_size)):
        users[i:i+batch_size].to_sql('account', con=engine, if_exists='append', index=False)

def seed_books():
    books = pd.read_csv("transformed/books.csv")
    batch_size = 5000
    for i in tqdm(range(0, len(books), batch_size)):
        books[i:i+batch_size].to_sql('book', con=engine, if_exists='append', index=False)

def seed_rating():
    ratings = pd.read_csv("transformed/ratings.csv")
    batch_size = 5000
    for i in tqdm(range(0, len(ratings), batch_size)):
        ratings[i:i+batch_size].to_sql('rating', con=engine, if_exists='append', index=False)


#clean books
'''
books = books[~books['Publisher'].isna()]
books = books[~books['ImageURL'].isna()]
books = books[~books['Author'].isna()]
ratings =  ratings[ratings["BookID"].isin(books["BookID"].values)]
'''

# print("seeding users...")
# seed_users()
print("seeding books...")
seed_books()
print("seeding ratings...")
seed_rating()

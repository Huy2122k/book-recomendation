import datetime
import uuid

import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from tqdm import tqdm

# engine = create_engine('mysql://root:1234@localhost/library')    
# df = pd.read_sql('SELECT * FROM book', engine) #read the entire table
# print(df.head())


MAP_USER = {}
MAP_BOOK = {}


def convert_age_to_birth(age):
    try:
        return datetime.datetime.now() - relativedelta(years=age)
    except:
        return datetime.datetime.now() - relativedelta(years=20)

def get_book_id(isbn):
    new_id = uuid.uuid4()
    MAP_BOOK[isbn] = new_id
    return new_id

def get_user_id(isbn):
    new_id = uuid.uuid4()
    MAP_USER[isbn] = new_id
    return new_id

def prepare_account():
    users = pd.read_csv("Users.csv")
    users["UserName"] = users["User-ID"].apply(lambda x: f"seed_user_{x}")
    users["AccountID"] = users["User-ID"].apply(get_user_id)
    users["Address"] = users["Location"]
    users["Birthday"] = users["Age"].apply(convert_age_to_birth)
    users = users.drop(columns=["User-ID", "Location", "Age"])

    sample_seed = {'AccountID': '0313d69d-886f-4890-be9e-ed49f3f01849', 'UserName': 'hwells', 'Password': '$2b$08$s9wCasH3AOlnyea1Lk0fx.LAx.5ELlrCeuoOqpuBnVfRM/b7.CRmu', 'Introduction': 'Cell wait think example for policy near mean alone here myself prove scene participant certain forward couple gun around stand always value letter democratic.', 'Gender': 'F', 'Birthday': '1935-06-13 00:00:00', 'Address': '51731 Perry Estates Apt. 566\nEast Regina, WA 34500', 'Phone': '394-71-5937', 'ImageURL': 'https://res.cloudinary.com/huyhuyhuy212/image/upload/v1674739545/userImage/0313d69d-886f-4890-be9e-ed49f3f01849.jpg', 'Role': 'USER', 'Status': 'available', 'EmailStatus': 'confirmed', 'Email': 'gregorybuck@gmail.com', 'IdentityStatus': 'confirmed', 'IdentityNum': '3534435447547784', 'FrontsideURL': 'https://t15.pimg.jp/046/801/725/1/46801725.jpg', 'BacksideURL': 'https://support.tradeapp.com/hc/article_attachments/360007170358/ID-back-EN.png', 'FaceURL': 'https://cdn3.vectorstock.com/i/1000x1000/65/97/man-head-avatar-beautiful-human-face-male-cartoon-vector-31176597.jpg', 'FullName': None}

    for key, val in sample_seed.items():
        if key not in users.columns:
            users[key] = val
    return users

def create_publish_date(year):
    try:
        year_num = int(year)
        if year_num <= 0:
            year_num = 1990
    except:
        year_num = 1990
    return datetime.datetime(year_num, 5, 17)

def prepare_book():
    book_ = pd.read_csv("Books.csv")

    books = pd.DataFrame()
    books["BookID"] = book_["ISBN"].apply(get_book_id)
    books["BookName"] = book_["Book-Title"]
    books['Author'] = book_["Book-Author"]
    books['PublishedDate'] = book_["Year-Of-Publication"].apply(create_publish_date)
    books['ImageURL'] = book_["Image-URL-L"]
    books['Series'] = "Series"
    books['Chapter'] = 2
    books['Description'] = "These friends, intimates since childhood, borrow money, beg favors, and, before even graduating college, they have created their first blockbuster, Ichigo. Overnight, the world is theirs. Not even twenty-five years old, Sam and Sadie are brilliant, successful, and rich, but these qualities won’t protect them from their own creative ambitions or the betrayals of their hearts."
    books['Price'] = 200
    books['Publisher'] = book_['Publisher'][:100]

    return books

def prepare_rating():
    ratings = pd.read_csv("Ratings.csv")
    old_columns = ratings.columns

    ratings["BookID"] = ratings["ISBN"].apply(lambda x: MAP_BOOK.get(x, None))
    ratings = ratings[ratings['BookID'].notna()]

    ratings["AccountID"] = ratings["User-ID"].apply(lambda x: MAP_USER.get(x, None))
    ratings["Rating"] = ratings["Book-Rating"].apply(lambda x: int(x/2))


    ratings = ratings.drop(columns=list(old_columns))

    return ratings


def prepare_data():
    print("prepare user...", datetime.datetime.now().strftime("%H:%M:%S"))
    users = prepare_account()
    print("prepare books...", datetime.datetime.now().strftime("%H:%M:%S"))
    books = prepare_book()
    print("prepare ratings...", datetime.datetime.now().strftime("%H:%M:%S"))
    ratings = prepare_rating()
    print("all done, writing data...")
    users.to_csv("transformed/users.csv", index=False)
    books.to_csv("transformed/books.csv", index=False)
    ratings.to_csv("transformed/ratings.csv", index=False)
    print("Save done!")


prepare_data()

# print("seeding...")

# engine = create_engine('mysql://root:1234@localhost/library')    

# users = prepare_account()
# batch_size = 5000
# for i in tqdm(range(0, len(users), batch_size)):
#     users[i:i+batch_size].to_sql('account', con=engine, if_exists='append', index=False)



print("successfully!")
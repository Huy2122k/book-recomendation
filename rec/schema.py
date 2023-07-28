import datetime
import uuid

import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine

engine = create_engine('mysql://root:1234@localhost/library')    
for name in engine.table_names():
    df = pd.read_sql(f'DESCRIBE {name}', engine) #read the entire table
    df = df[["Field", "Type", "Null", "Extra"]]
    df = df.rename(columns={"Field": "Tên trường", "Type": "Kiểu dữ liệu", "Null": "Nullable", "Extra":"Mô tả"})
    df["Nullable"] = df["Nullable"].apply(lambda x: x.lower())

    df.to_csv(f"schema/{name}.csv", index=False)

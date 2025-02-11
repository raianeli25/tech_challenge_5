import os
import pandas as pd
from fastapi import FastAPI
from utils.db_conn import MongoDBConn
from model.data_treatment import function_test

app = FastAPI()

@app.get('/')
def route_default():
    return 'Welcome to API'

@app.post('/post_data_into_db')
def post_data_into_db(data_path):
    db = MongoDBConn()
    df = pd.read_csv(data_path)
    db_name = data_path.split('/')[-1].split('.')[0]
    if df.bool:
        db.insert_data(db_name, df)
        return 'Sucesso'
    else:
        return 'Sem dados'

# @app.get('/recommendation')
# def get_recommendation(
#     recommendation: Recommendation
# ):
#     df = test.call_df()
#     return df
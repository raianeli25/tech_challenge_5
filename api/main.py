import os

from fastapi import FastAPI
from utils.db_conn import MongoDBConn
from model.data_treatment import function_test

app = FastAPI()

@app.get('/')
def route_default():
    return 'Welcome to API'

@app.get('/get_data_into_db')
def get_data_into_db(db_name):
    db = MongoDBConn()
    df = function_test()
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
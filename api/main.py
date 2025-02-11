import os
import pandas as pd
from fastapi import FastAPI
from utils.db_conn import MongoDBConn
from utils.recommendation import sample_recommendation
import pickle

app = FastAPI()

db = MongoDBConn()

loaded_model = pickle.load(open('artifacts/lightfm_model.pkl', 'rb'))
loaded_user_id_map = pickle.load(open('artifacts/user_id_map.pkl', 'rb'))
loaded_item_id_map_reverse = pickle.load(open('artifacts/item_id_map_reverse.pkl', 'rb'))
loaded_user_feature_map = pickle.load(open('artifacts/user_feature_map.pkl', 'rb'))

@app.get('/')
def route_default():
    return 'Welcome to API'

@app.post('/post_data_into_db')
def post_data_into_db(data_path):
    df = pd.read_csv(data_path)
    db_name = data_path.split('/')[-1].split('.')[0]
    if df.bool:
        db.insert_data(db_name, df)
        return 'Sucesso'
    else:
        return 'Sem dados'

@app.post('/recommendation')
def get_recommendation(user_hash):

    return sample_recommendation(user_hash,loaded_item_id_map_reverse,loaded_user_feature_map,loaded_user_id_map,loaded_model)
    
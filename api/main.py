import pickle
import pandas as pd
from fastapi import FastAPI

from utils.db_conn import MongoDBConn
from utils.custom_data_structs import UserItemData
from utils.model_funcs import recommend_by_model_scores, get_user_item_data

app = FastAPI()

db = MongoDBConn()

loaded_model = pickle.load(open('artifacts/lightfm_model.pkl', 'rb'))
loaded_user_item_data:UserItemData = get_user_item_data()

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
    ## !! AQUI !! ONLY RECOMMENDATION BY SCORES - NEED TO ADD POPULATIRY AND RANDOM!
    return recommend_by_model_scores(user_hash,loaded_user_item_data,loaded_model)
    
import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException
from pathlib import Path

from utils.db_conn import MongoDBConn
from utils.custom_data_structs import UserItemData
from utils.model_funcs import recommend_by_model_scores, read_popular_dict_into_list, read_random_dict_into_list

import __main__
def getImages(d): return##
__main__.UserItemData = UserItemData


app = FastAPI()

db = MongoDBConn()

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"

try:
    loaded_model = pickle.load(open(ARTIFACTS_DIR / "lightfm_model.pkl", "rb"))
    loaded_dict_popular_histories = pickle.load(open(ARTIFACTS_DIR / "dict_popular_histories.pkl", "rb"))
    loaded_dict_random_histories = pickle.load(open(ARTIFACTS_DIR / "dict_random_histories.pkl", "rb"))
    loaded_user_item_data: UserItemData = pickle.load(open(ARTIFACTS_DIR / "user_item_data.pkl", "rb"))
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error loading models or data: {str(e)}")

top_k_popular = read_popular_dict_into_list(loaded_dict_popular_histories["history"])

@app.get('/')
def route_default():
    return 'Welcome to API'

@app.post('/post_data_into_db')
def post_data_into_db(data_path):
    
    try:
        df = pd.read_csv(data_path)
        db_name = data_path.split('/')[-1].split('.')[0]
        if df.bool:
            db.insert_data(db_name, df)
            return 'Data successfully inserted into the database'
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="The CSV file is empty")

@app.post('/recommendation_history_hash')
def get_recommendation(user_hash):

    try:
        random_k_histories = read_random_dict_into_list(loaded_dict_random_histories["history"])
        model_histories = recommend_by_model_scores(user_hash,loaded_user_item_data,loaded_model)
        recommendation_list =  model_histories + top_k_popular + random_k_histories
        return list(set(recommendation_list))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post('/recommendation')
def get_recommendation(user_hash):
    
    try:
        random_k_histories = read_random_dict_into_list(loaded_dict_random_histories["history"])
        model_histories = recommend_by_model_scores(user_hash,loaded_user_item_data,loaded_model)
        recommendation_list =  model_histories + top_k_popular + random_k_histories
        return db.get_titles_by_item_ids(list(set(recommendation_list)))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


    
import numpy as np
import pandas as pd
from scipy import sparse
from utils.db_conn import MongoDBConn

db = MongoDBConn()

def format_newuser_input(user_feature_map, user_feature_list):
  normalised_val = 1.0 
  target_indices = []
  for feature in user_feature_list:
    try:
        target_indices.append(user_feature_map[feature])
    except KeyError:
        print("new user feature encountered '{}'".format(feature))
        pass
  #print("target indices: {}".format(target_indices))
  new_user_features = np.zeros(len(user_feature_map.keys()))
  for i in target_indices:
    new_user_features[i] = normalised_val
  new_user_features = sparse.csr_matrix(new_user_features)
  return(new_user_features)

def sample_recommendation(user_hash,item_id_map_reverse,user_feature_map,user_id_map,model):
    try:
        user_x = user_id_map[user_hash]
        scores = model.predict(user_x, np.arange(108573)) # means predict for all
    except:
        user_feature_list = ['Non-Logged']
        new_user_features = format_newuser_input(user_feature_map, user_feature_list)
        scores = model.predict(0, np.arange(108573), user_features=new_user_features)
    
    top_5_indices = np.argsort(-scores)[:5]  # Sort scores in descending order and take the top 5
    top_5_items = [item_id_map_reverse[i] for i in top_5_indices]

    recommendation = []

    for x in top_5_items:
        item = db.get_item_by_id('noticias_final_v2',x)
        recommendation.append(item['title'])

    return recommendation
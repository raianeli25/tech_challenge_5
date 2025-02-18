import random
import pickle

import numpy as np
import pandas as pd
from scipy import sparse

from lightfm import LightFM

from utils.custom_data_structs import UserItemData


SEED = 42
K_LIGHTFM_ITEMS = 6
K_POPULAR_ITEMS = 6
K_SAMPLED_ITEMS = 3

random.seed(SEED)

loaded_user_item_data:UserItemData = pickle.load(open('artifacts/user_item_data.pkl', 'rb'))
loaded_n_users, loaded_n_items = loaded_user_item_data.interactions_shape

def get_user_item_data() -> UserItemData:
      return loaded_user_item_data



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

def get_scores_from_model(user_hash:str,user_feature_list:list|str,user_item_data:UserItemData,model:LightFM):
    """
    This function 
    """
    if isinstance(user_feature_list, str):
        user_feature_list = [user_feature_list]
    try:
        user_x = user_item_data.user_id_map[user_hash]
        scores = model.predict(user_x, np.arange(loaded_n_items)) # means predict for all
    except:
        new_user_features = format_newuser_input(user_item_data.user_feature_map, user_feature_list)
        scores = model.predict(0, np.arange(loaded_n_items), user_features=new_user_features)
    return scores

def get_top_items_by_model_scores(scores, user_item_data):
    """
    This function verifies if the users is known or new, and makes recommendations depending on this verification.
    The top K_LIGHTFM_ITEMS recommendations from the list are returned.
    """
    
    top_k_indices = np.argsort(-scores)[:K_LIGHTFM_ITEMS]  # Sort scores in descending order and take the top K_ITEMS
    return [user_item_data.item_id_map_reverse[i] for i in top_k_indices]

def recommend_by_model_scores(user_hash:str,user_feature_list:list|str,user_item_data:UserItemData,model:LightFM):
    """
    This function 
    """
    
    scores = get_scores_from_model(user_hash,user_feature_list,user_item_data,model)
    return get_top_items_by_model_scores(scores, user_item_data)

def count_histories_by_popularity(df:pd.DataFrame):
    """
    This function 
    """
    
    return df.groupby(["history"]).size().sort_values(ascending=False).astype(dtype="UInt16")

def get_df_most_popular_histories(df_count_histories:pd.DataFrame):
    return df_count_histories.iloc[:K_POPULAR_ITEMS]

def get_df_most_unpopular_histories(df_count_histories:pd.DataFrame):
    return df_count_histories.iloc[K_POPULAR_ITEMS:]

def recommend_by_most_popular(df:pd.DataFrame):
    """
    This function 
    """
    df_count_histories = count_histories_by_popularity(df)
    df_popular_stories = get_df_most_popular_histories(df_count_histories)
    return list(set(df_popular_stories.keys()))

def recommend_by_weighted_random(df_unpopular_histories:pd.DataFrame, unpopular_weights:list):
    """
    This function 
    """
    random_k_histories = df_unpopular_histories.sample(n=K_SAMPLED_ITEMS, weights=unpopular_weights, random_state=random.randint(0, 50))
    # return random_k_histories
    return list(set(random_k_histories.keys()))

def order_df_by_most_recent(df:pd.DataFrame, history_list:list):
    return df[df["history"].isin(history_list)].sort_values("age_exp_normalized",ascending=False)

    
def list_intersection(list1:list, list2:list):
    return list(set(list1) & set(list2))
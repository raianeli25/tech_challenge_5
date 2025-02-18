import random
import pickle

import numpy as np
import pandas as pd
from scipy import sparse

from lightfm import LightFM

from utils.custom_data_structs import UserItemData
from utils.db_conn import MongoDBConn

db = MongoDBConn()

SEED = 42
K_LIGHTFM_ITEMS = 6
K_POPULAR_ITEMS = 6
K_SAMPLED_ITEMS = 3

random.seed(SEED)

loaded_user_item_data:UserItemData = pickle.load(open('artifacts/user_item_data.pkl', 'rb'))
loaded_n_users, loaded_n_items = loaded_user_item_data.interactions_shape


def get_user_item_data() -> UserItemData:
    """
    Simple get function to return "loaded_user_item_data", 
    loaded from pickle file.
    """  
    return loaded_user_item_data



def format_newuser_input(user_feature_map:dict, user_feature_list:list)->sparse.csr_matrix:
    """
    This function receives a 'user_feature_list' and its mapping 'user_feature_map'.
    It is used to create a sparse matrix representation for user_feature presence.
    """
    normalised_val = 1.0
    target_indices = []
    for feature in user_feature_list:
        # try to make the mapping from user_feature_list -> indexes
        try:
            target_indices.append(user_feature_map[feature])
        # if it does not exist, just pass (ignore)
        except KeyError:
            print("new user feature encountered '{}'".format(feature))
            pass
    # initialize a vector [0 0 0 0 0 ... 0]
    new_user_features = np.zeros(len(user_feature_map.keys()))
    # for the found indexes above, change the entry to normalised_val (1.0)
    for i in target_indices:
        new_user_features[i] = normalised_val
    # transform into sparse matrix and return
    new_user_features = sparse.csr_matrix(new_user_features)
    return(new_user_features)



def get_scores_from_model(user_hash:str,user_item_data:UserItemData,model:LightFM):
    """
    This function receives a user_hash and generates a full array of scores for recommendation.
    The scores array have size equal to `loaded_n_items`, i.e., the number of items used for training.
    """

    # try to recommend for known users
    try:
        user_x = user_item_data.user_id_map[user_hash]
        scores = model.predict(user_x, np.arange(loaded_n_items))
    # recommend for new/unknown user
    except:
        user_feature_list = ['Non-Logged']
        new_user_features = format_newuser_input(user_item_data.user_feature_map, user_feature_list)
        scores = model.predict(0, np.arange(loaded_n_items), user_features=new_user_features)
    return scores



def get_top_items_by_model_scores(scores, user_item_data):
    """
    The top K_LIGHTFM_ITEMS recommendations from the list are returned.
    """
    
    top_k_indices = np.argsort(-scores)[:K_LIGHTFM_ITEMS]  # Sort scores in descending order and take the top K_ITEMS
    return [user_item_data.item_id_map_reverse[i] for i in top_k_indices]



def recommend_by_model_scores(user_hash:str,user_item_data:UserItemData,model:LightFM):
    """
    This function is just a wrapper to call both get_scores_from_model()
    and get_top_items_by_model_scores() in sequence.
    """
    
    scores = get_scores_from_model(user_hash,user_item_data,model)
    return get_top_items_by_model_scores(scores, user_item_data)



def count_histories_by_popularity(df:pd.DataFrame, item_column:str="history")->pd.DataFrame:
    """
    This function receives a dataframe containing the item_column
    and returns the number of occurences of such item in the dataset.
    Also, the counts are ordered descending (greater first).
    """
    
    return df.groupby([item_column]).size().sort_values(ascending=False).astype(dtype="UInt16")



def get_df_most_popular_histories(df_count_histories:pd.DataFrame, k_pop_items:int=K_POPULAR_ITEMS)->pd.DataFrame:
    """
    Considering an ordered (descending) dataset, 
    recommends the k_pop_items rows with most counts.
    """
    return df_count_histories.iloc[:k_pop_items]



def get_df_most_unpopular_histories(df_count_histories:pd.DataFrame, k_pop_items:int=K_POPULAR_ITEMS)->pd.DataFrame:
    """
    Considering an ordered (descending) dataset, 
    recommends all the remaining rows from df_count_histories, except the
    first k_pop_items rows.
    """
    return df_count_histories.iloc[k_pop_items:]



def recommend_by_most_popular(df:pd.DataFrame)->list:
    """
    This function is a wrapper to get most popular items.
    """
    df_count_histories = count_histories_by_popularity(df)
    df_popular_stories = get_df_most_popular_histories(df_count_histories)
    return list(set(df_popular_stories.keys()))



def recommend_by_weighted_random(df_unpopular_histories:pd.DataFrame, unpopular_weights:list, k_sample_items:int=K_SAMPLED_ITEMS)->list:
    """
    This function will select randomly `k_sample_items` from `df_unpopular_histories`.
    The probability of an item to be selected is proportional to `unpopular_weights`.
    Thus, most popular items have more probability to be selected (by not guarantees -> random!)
    """
    random_k_histories = df_unpopular_histories.sample(n=k_sample_items, weights=unpopular_weights, random_state=random.randint(0, 50))
    # return random_k_histories
    return list(set(random_k_histories.keys()))



def list_intersection(list1:list, list2:list)->list:
    """
    Given lists `list1` and `list2`, return the intersection of their items.
    Example: 
    list1 = ['a', 'b', 'c', 'd']
    list1 = ['c', 'd', 'e']
    Then, the return is ['c', 'd']
    """
    return list(set(list1) & set(list2))

def get_titles_from_ids(item_ids_list:list, db_name:str="noticias_final_v2")->list:
    """
    Given a list item_ids_list, get the respective titles from database "db".
    """
    recommendation = []
    for item_id in item_ids_list:
        item = db.get_item_by_id(db_name,item_id)
        recommendation.append(item['title'])
    return recommendation
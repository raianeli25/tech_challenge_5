import random
import pickle

import numpy as np
import pandas as pd
from scipy import sparse

from lightfm import LightFM

from utils.custom_data_structs import UserItemData


SEED = 42
K_LIGHTFM_ITEMS = 7
K_POPULAR_ITEMS = 7
K_UNPOPULAR_ITEMS = 1000
K_SAMPLED_ITEMS = 6

COUNT_TO_ABANDON_THRESHOLD = 15
FRESHNESS_THRESHOLD = 0.95

random.seed(SEED)


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
        if user_hash == 'fff46e72c87ef6d8e149b0a60f3346a84256b2d30c04bc53261f32cfff8af069':
            print("try")
        user_x = user_item_data.user_id_map[user_hash]
        if user_hash == 'fff46e72c87ef6d8e149b0a60f3346a84256b2d30c04bc53261f32cfff8af069':
            print(f"{user_x}")
        scores = model.predict(user_x, np.arange(user_item_data.interactions_shape[1]))
        if user_hash == 'fff46e72c87ef6d8e149b0a60f3346a84256b2d30c04bc53261f32cfff8af069':
            print(f"{scores}")
    # recommend for new/unknown user
    except:
        if user_hash == 'fff46e72c87ef6d8e149b0a60f3346a84256b2d30c04bc53261f32cfff8af069':
            print("except")
            print(f"{user_hash}")
        user_feature_list = ['Non-Logged']
        new_user_features = format_newuser_input(user_item_data.user_feature_map, user_feature_list)
        if user_hash == 'fff46e72c87ef6d8e149b0a60f3346a84256b2d30c04bc53261f32cfff8af069':
            print(f"{new_user_features}")
        scores = model.predict(0, np.arange(user_item_data.interactions_shape[1]), user_features=new_user_features)
        if user_hash == 'fff46e72c87ef6d8e149b0a60f3346a84256b2d30c04bc53261f32cfff8af069':
            print(f"{scores}")
    
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
    # if user_hash == 'fff46e72c87ef6d8e149b0a60f3346a84256b2d30c04bc53261f32cfff8af069':
    #         print(f"{scores}")
    # top_k = get_top_items_by_model_scores(scores, user_item_data)
    # if user_hash == 'fff46e72c87ef6d8e149b0a60f3346a84256b2d30c04bc53261f32cfff8af069':
    #         print(f"{top_k}")
    # return top_k



def count_histories_by_popularity(df:pd.DataFrame, 
                                  item_column:str="history", 
                                  sort_by_column:str="historyFreshnessNormalized")->pd.Series:
    """
    This function receives a dataframe containing the item_column
    and returns the number of occurences of such item in the dataset.
    Also, the counts are ordered descending (greater first).
    """
    
    return df.groupby([item_column,sort_by_column]).size().sort_values(ascending=False).astype(dtype="UInt16").to_frame(name="counts").reset_index()


def get_dict_most_popular_histories(df_count_histories:pd.DataFrame, k_pop_items:int=K_POPULAR_ITEMS)->dict:
    """
    Considering an ordered (descending) dataset, 
    recommends the k_pop_items rows with most counts.
    """
    return df_count_histories.iloc[:k_pop_items].to_dict()


def get_df_most_popular_histories(df_count_histories:pd.DataFrame, k_pop_items:int)->pd.DataFrame:
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



def recommend_by_most_popular(df:pd.DataFrame,k_pop_items:int=K_POPULAR_ITEMS)->list:
    """
    This function is a wrapper to get most popular items.
    """
    df_count_histories = count_histories_by_popularity(df)
    df_popular_stories = get_df_most_popular_histories(df_count_histories,k_pop_items)
    return list(set(df_popular_stories.keys()))



def recommend_by_weighted_random_old(df_unpopular_histories:pd.DataFrame, unpopular_weights:list, k_sample_items:int=K_SAMPLED_ITEMS)->list:
    """
    This function will select randomly `k_sample_items` from `df_unpopular_histories`.
    The probability of an item to be selected is proportional to `unpopular_weights`.
    Thus, most popular items have more probability to be selected (by not guarantees -> random!)
    """
    random_k_histories = df_unpopular_histories.sample(n=k_sample_items, weights=unpopular_weights, random_state=random.randint(0, 50))
    return list(set(random_k_histories.keys()))



def filter_old_and_abandoned_histories(df_unpopular:pd.DataFrame)->list:
    """
    This function will select randomly `k_sample_items` from `df_unpopular_histories`.
    The probability of an item to be selected is proportional to `unpopular_weights`.
    Thus, most popular items have more probability to be selected (by not guarantees -> random!)
    """
    df_unpopular = df_unpopular[df_unpopular["counts"] > COUNT_TO_ABANDON_THRESHOLD]
    return df_unpopular[df_unpopular["historyFreshnessNormalized"] > FRESHNESS_THRESHOLD]


def get_df_random_histories(df_count_histories:pd.DataFrame, k_sample_items:int=K_UNPOPULAR_ITEMS)->list:
    """
    This function will select randomly `k_sample_items` from `df_unpopular_histories`.
    The probability of an item to be selected is proportional to `unpopular_weights`.
    Thus, most popular items have more probability to be selected (by not guarantees -> random!)
    """
    df_unpopular = get_df_most_unpopular_histories(df_count_histories, k_sample_items)
    df_random = filter_old_and_abandoned_histories(df_unpopular)
    return df_random.sample(k_sample_items,weights=df_count_histories["counts"],random_state=SEED)


def get_dict_random_histories(df_random:pd.DataFrame)->dict:
    """
    Considering an ordered (descending) dataset, 
    recommends the k_pop_items rows with most counts.
    """
    return df_random.to_dict()


def read_popular_dict_into_list(populars:dict):

    return list(populars.values())


def read_random_dict_into_list(randoms_dict:dict):

    random_history_list = list(randoms_dict.values())
    return random.sample(random_history_list,K_SAMPLED_ITEMS)


def list_intersection(list1:list, list2:list)->list:
    """
    Given lists `list1` and `list2`, return the intersection of their items.
    Example: 
    list1 = ['a', 'b', 'c', 'd']
    list1 = ['c', 'd', 'e']
    Then, the return is ['c', 'd']
    """
    return list(set(list1) & set(list2))

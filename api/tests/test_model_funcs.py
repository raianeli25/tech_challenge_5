import pytest
import random
import numpy as np
import pandas as pd
from scipy import sparse
from unittest.mock import MagicMock

from lightfm import LightFM
from utils.custom_data_structs import UserItemData

from utils.model_funcs import (
    format_newuser_input,
    get_scores_from_model,
    get_top_items_by_model_scores,
    recommend_by_model_scores,
    count_histories_by_popularity,
    get_dict_most_popular_histories,
    get_df_most_popular_histories,
    get_df_most_unpopular_histories,
    recommend_by_most_popular,
    filter_old_and_abandoned_histories,
    get_df_random_histories,
    get_dict_random_histories,
    read_popular_dict_into_list,
    read_random_dict_into_list,
    list_intersection
)

SEED = 42  
K_SAMPLED_ITEMS = 6  
K_UNPOPULAR_ITEMS = 10
K_POP_ITEMS = 3

def test_format_newuser_input():

    user_feature_map = {"feature1": 0, "feature2": 1}
    user_feature_list = ["feature1", "feature2"]
    
    result = format_newuser_input(user_feature_map, user_feature_list)
    
    assert result.shape == (1, 2)
    assert result[0, 0] == 1.0
    assert result[0, 1] == 1.0

def test_get_scores_from_model():

    mock_user_item_data = MagicMock()
    mock_user_item_data.user_id_map = {"user123": 0}
    mock_user_item_data.interactions_shape = (1, 10)
    
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0.1, 0.5, 0.9, 0.3, 0.2])

    scores = get_scores_from_model("user123", mock_user_item_data, mock_model)
    
    assert len(scores) == 5
    mock_model.predict.assert_called()

def test_get_top_items_by_model_scores():

    mock_user_item_data = MagicMock()
    mock_user_item_data.item_id_map_reverse = {0: "itemA", 1: "itemB", 2: "itemC"}

    scores = np.array([0.2, 0.8, 0.5])
    
    result = get_top_items_by_model_scores(scores, mock_user_item_data)

    assert result == ["itemB", "itemC", "itemA"]

def test_recommend_by_model_scores():
    user_item_data = MagicMock()
    model = MagicMock()
    model.predict.return_value = np.array([0.9, 0.5, 0.3])

    user_item_data.item_id_map_reverse = {0: "itemA", 1: "itemB", 2: "itemC"}

    result = recommend_by_model_scores("user123", user_item_data, model)

    assert isinstance(result, list)
    assert len(result) <= 7
    assert "itemA" in result

def test_count_histories_by_popularity():
    data = {"history": ["A", "B", "A", "C", "C", "C"], "historyFreshnessNormalized": [0.9, 0.8, 0.9, 0.7, 0.7, 0.7]}
    df = pd.DataFrame(data)

    result = count_histories_by_popularity(df)

    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0]["history"] == "C"

def test_get_dict_most_popular_histories():
    data = {
        "history": ["A", "B", "C", "D", "E"],
        "counts": [100, 80, 60, 40, 20]
    }
    df_count_histories = pd.DataFrame(data)

    result = get_dict_most_popular_histories(df_count_histories, k_pop_items=3)

    assert isinstance(result, dict)
    assert len(result["history"]) == 3
    assert result["history"][0] == "A"
    assert result["counts"][0] == 100

def test_get_df_most_popular_histories():
    data = {
        "history": ["A", "B", "C", "D", "E"],
        "counts": [100, 80, 60, 40, 20]
    }
    df_count_histories = pd.DataFrame(data)

    result = get_df_most_popular_histories(df_count_histories, K_POP_ITEMS)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == K_POP_ITEMS
    assert list(result["history"]) == ["A", "B", "C"]  
    assert list(result["counts"]) == [100, 80, 60]

def test_get_df_most_unpopular_histories():
    data = {
        "history": ["A", "B", "C", "D", "E"],
        "counts": [100, 80, 60, 40, 20]
    }
    df_count_histories = pd.DataFrame(data)

    result = get_df_most_unpopular_histories(df_count_histories, K_POP_ITEMS)

    assert isinstance(result, pd.DataFrame) 
    assert len(result) == len(df_count_histories) - K_POP_ITEMS 
    assert list(result["history"]) == ["D", "E"] 
    assert list(result["counts"]) == [40, 20] 

def test_recommend_by_most_popular():

    data = {
        "history": ["A", "B", "C", "D", "E"],
        "historyFreshnessNormalized": [0.9, 0.8, 0.7, 0.6, 0.5]
    }
    df = pd.DataFrame(data)

    result = recommend_by_most_popular(df, K_POP_ITEMS)

    assert isinstance(result, list)  
    assert len(result) == K_POP_ITEMS

def test_filter_old_and_abandoned_histories():

    data = {
        "history": ["A", "B", "C", "D", "E"],
        "counts": [20, 10, 30, 5, 50],
        "historyFreshnessNormalized": [0.96, 0.90, 0.98, 0.80, 0.99]
    }
    df_unpopular = pd.DataFrame(data)

    result_df = filter_old_and_abandoned_histories(df_unpopular)

    assert isinstance(result_df, pd.DataFrame)

    expected_histories = ["A", "C", "E"]
    assert list(result_df["history"]) == expected_histories

def test_get_df_random_histories():

    data = {
        "history": [f"Item_{i}" for i in range(1, 51)],
        "counts": [i for i in range(1, 51)],
        "historyFreshnessNormalized": [0.6 if i % 2 == 0 else 1.0 for i in range(1, 51)]
    }
    df_count_histories = pd.DataFrame(data)

    df_unpopular = df_count_histories[
        (df_count_histories["counts"] > 15) & 
        (df_count_histories["historyFreshnessNormalized"] > 0.95)
    ]

    num_available_items = len(df_unpopular)

    k_sample = min(K_UNPOPULAR_ITEMS, num_available_items)

    result_df = get_df_random_histories(df_count_histories, k_sample)

    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == k_sample
    assert set(result_df["history"]).issubset(set(df_unpopular["history"]))
    assert all(result_df["counts"] > 15)
    assert all(result_df["historyFreshnessNormalized"] > 0.95)

def test_get_dict_random_histories():

    data = {
        "history": ["Item_1", "Item_2", "Item_3"],
        "counts": [10, 20, 30],
        "historyFreshnessNormalized": [0.8, 0.95, 1.0]
    }
    df_random = pd.DataFrame(data)

    result_dict = get_dict_random_histories(df_random)

    assert isinstance(result_dict, dict)
    assert set(result_dict.keys()) == set(df_random.columns)

    for column in df_random.columns:
        assert list(result_dict[column].values()) == list(df_random[column])

def test_read_popular_dict_into_list():
    populars = {
        "item_1": 101,
        "item_2": 202,
        "item_3": 303
    }

    result_list = read_popular_dict_into_list(populars)

    assert isinstance(result_list, list)
    assert result_list == list(populars.values())

def test_read_random_dict_into_list():
    random.seed(SEED)
    randoms_dict = {
        "item_1": 101, "item_2": 202, "item_3": 303,
        "item_4": 404, "item_5": 505, "item_6": 606,
        "item_7": 707, "item_8": 808, "item_9": 909,
        "item_10": 1000
    }

    result_list = read_random_dict_into_list(randoms_dict)

    assert isinstance(result_list, list)
    assert len(result_list) == K_SAMPLED_ITEMS
    assert all(item in randoms_dict.values() for item in result_list)

def test_list_intersection():
    list1 = ['a', 'b', 'c', 'd']
    list2 = ['c', 'd', 'e']
    assert set(list_intersection(list1, list2)) == {'c', 'd'}

    list1 = ['x', 'y', 'z']
    list2 = ['a', 'b', 'c']
    assert list_intersection(list1, list2) == []

    assert list_intersection([], []) == []

    assert list_intersection(['a', 'b', 'c'], ['']) == []
    assert list_intersection([''], ['a', 'b', 'c']) == []

    list1 = ['a', 'b', 'c']
    list2 = ['a', 'b', 'c']
    assert set(list_intersection(list1, list2)) == {'a', 'b', 'c'}
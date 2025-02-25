import numpy as np
from unittest.mock import MagicMock
from utils.model_funcs import (
    format_newuser_input,
    get_scores_from_model,
    get_top_items_by_model_scores,
)

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
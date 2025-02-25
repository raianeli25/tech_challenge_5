import pytest
from unittest.mock import MagicMock, patch
from utils.db_conn import MongoDBConn

@pytest.fixture
def mock_mongo():
    with patch("utils.db_conn.MongoClient") as mock_client:
        yield mock_client

def test_insert_data(mock_mongo):
    mock_db = mock_mongo.return_value["db_model"]["test_collection"]
    mock_db.insert_many.return_value = None

    mongo_conn = MongoDBConn()
    mock_df = MagicMock()
    mock_df.to_dict.return_value = [{"_id": 1, "page": "test_page"}]
    
    mongo_conn.insert_data("test_collection", mock_df)
    mock_db.insert_many.assert_called_once()

def test_get_item_by_id(mock_mongo):

    mock_db = mock_mongo.return_value["db_model"]["test_collection"]
    mock_db.find_one.return_value = {"_id": "123", "title": "Test Item"}

    mongo_conn = MongoDBConn()
    result = mongo_conn.get_item_by_id("test_collection", "123")
    
    assert result is not None
    assert result["title"] == "Test Item"

def test_get_titles_by_item_ids(mock_mongo):

    mock_db = mock_mongo.return_value["db_model"]["full_items"]
    mock_db.find_one.side_effect = [{"_id": "1", "title": "Title 1"}, {"_id": "2", "title": "Title 2"}]

    mongo_conn = MongoDBConn()
    result = mongo_conn.get_titles_by_item_ids(["1", "2"])

    assert result == ["Title 1", "Title 2"]
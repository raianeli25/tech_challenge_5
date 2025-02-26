import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import pandas as pd

client = TestClient(app)

@pytest.fixture
def mock_mongo():
    """Cria um mock da conexão com MongoDB."""
    with patch("utils.db_conn.MongoClient") as mock_client:
        yield mock_client

def test_route_default():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == 'Welcome to API'

@pytest.mark.parametrize("data_path", ["tests/sample_data.csv"])
def test_post_data_into_db(mocker, data_path):
    mock_insert = mocker.patch("utils.db_conn.MongoDBConn.insert_data", return_value=None)
    mock_read_csv = mocker.patch("pandas.read_csv", return_value=pd.DataFrame({'col': [1, 2, 3]}))
    
    response = client.post(f'/post_data_into_db?data_path={data_path}')
    
    assert response.status_code == 200
    assert response.json() == "Data successfully inserted into the database"
    mock_insert.assert_called_once()
    mock_read_csv.assert_called_once_with(data_path)

def test_post_data_into_db_no_data(mocker):
    mocker.patch("pandas.read_csv", return_value=pd.DataFrame()) 
    data_path = "tests/sample_data.csv"
    response = client.post(f'/post_data_into_db?data_path={data_path}')

    assert response.status_code == 400
    assert response.json()['detail'] == "The CSV file is empty"

@pytest.mark.parametrize("user_hash", ["user_123", "user_456"])
def test_recommendation(mocker, user_hash, mock_mongo):

    mock_recommend = mocker.patch("main.recommend_by_model_scores", return_value=["rec1", "rec2"])
    mock_read_random = mocker.patch("main.read_random_dict_into_list", return_value=["rand1", "rand2"])
    
    mock_db_conn = mocker.patch("main.db.get_titles_by_item_ids", return_value=["Title1", "Title2"])

    response = client.post(f'/recommendation?user_hash={user_hash}')
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json() == ["Title1", "Title2"]
    mock_recommend.assert_called_once_with(user_hash, mocker.ANY, mocker.ANY)
    mock_read_random.assert_called_once_with(mocker.ANY)
    mock_db_conn.assert_called_once()

def test_model_loading_failure(monkeypatch):
    def mock_pickle_load(*args, **kwargs):
        raise Exception("Failed to load model")

    monkeypatch.setattr("pickle.load", mock_pickle_load)

    response = client.post(f'/recommendation?user_hash=test_user')
    
    assert response.status_code == 500
    assert "Error generating recommendations" in response.json()["detail"]

def test_recommendation_exception(monkeypatch):
    def mock_recommend_by_model_scores(*args, **kwargs):
        raise Exception("Model failure")

    monkeypatch.setattr("main.recommend_by_model_scores", mock_recommend_by_model_scores)

    response = client.post(f'/recommendation?user_hash=test_user')

    assert response.status_code == 500
    assert "Error generating recommendations" in response.json()["detail"]

@pytest.mark.parametrize("user_hash", ["user_123", "user_456"])
def test_recommendation_history_hash(mocker, user_hash):
    mock_recommend = mocker.patch("main.recommend_by_model_scores", return_value=["rec1", "rec2"])
    mock_read_random = mocker.patch("main.read_random_dict_into_list", return_value=["rand1", "rand2"])
    
    response = client.post(f'/recommendation_history_hash?user_hash={user_hash}')

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    mock_recommend.assert_called_once_with(user_hash, mocker.ANY, mocker.ANY)
    mock_read_random.assert_called_once_with(mocker.ANY)

def test_recommendation_history_hash_exception(monkeypatch):
    def mock_recommend_by_model_scores(*args, **kwargs):
        raise Exception("Model failure")

    monkeypatch.setattr("main.recommend_by_model_scores", mock_recommend_by_model_scores)

    response = client.post(f'/recommendation_history_hash?user_hash=test_user')
    
    assert response.status_code == 500
    assert "Error generating recommendations" in response.json()["detail"]


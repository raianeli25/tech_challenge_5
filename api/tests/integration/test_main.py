import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_route_default():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == 'Welcome to API'

# @pytest.mark.parametrize("data_path", ["tests/sample_data.csv"])
# def test_post_data_into_db(mocker, data_path):
#     mock_insert = mocker.patch("utils.db_conn.MongoDBConn.insert_data", return_value=None)
#     mock_read_csv = mocker.patch("pandas.read_csv", return_value=pd.DataFrame({'col': [1, 2, 3]}))
    
#     response = client.post('/post_data_into_db', json={"data_path": data_path})
    
#     assert response.status_code == 200
#     assert response.json() == "Sucesso"
#     mock_insert.assert_called_once()
#     mock_read_csv.assert_called_once_with(data_path)

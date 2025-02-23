import pytest
import requests
import os
import pandas as pd
from api.utils.db_conn import MongoDBConn

@pytest.fixture
def mongo_instance():
    db = MongoDBConn()
    yield db
    db.client.close()  

@pytest.fixture
def setup_test_csv():

    test_csv_path = "data/test_data.csv"
    df = pd.DataFrame({"page": [1, 2, 3], "value": [100, 200, 300]})
    df.to_csv(test_csv_path, index=False)
    yield test_csv_path
    os.remove(test_csv_path)

def test_post_data_into_db(setup_test_csv, mongo_instance):

    test_csv_path = setup_test_csv
    client = mongo_instance

    response = requests.post(
        f'http://localhost:8000/post_data_into_db?data_path={test_csv_path}'
    )
    assert response.status_code == 200
    assert response.json() == "Sucesso"

    db = client.get_database('db_test')
    assert db.name == 'db_test'

    # client.drop_database('db_test')
    # inserted_data = list(db['test_data'].find())
    # assert len(inserted_data) == 3

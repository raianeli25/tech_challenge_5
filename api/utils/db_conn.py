from pymongo import MongoClient

class MongoDBConn:
    def __init__(self, host='mongo', port=27017, username='root', password='root', authSource='admin'):
        
        self.client = MongoClient(
            f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}'
        )
        
    def insert_data(self, db_name: str, df):
        db = self.client["db_model"]
        db_collect = db[db_name]
        data = df.to_dict(orient='records')
        db_collect.insert_many(data)


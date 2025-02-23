from pymongo import MongoClient

class MongoDBConn:
    def __init__(self, host='mongo', port=27017, username='root', password='root', authSource='admin'):
        
        self.client = MongoClient(
            f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}'
        )

    def insert_data(self, db_name: str, df):

        if db_name == 'test_data':
            db = self.client["db_test"]
        else:
            db = self.client["db_model"]
        db_collect = db[db_name]
        df['_id'] = df['page'] 
        data = df.to_dict(orient='records')
        db_collect.insert_many(data)
    
    def get_database(self, db_name):
        return self.client[db_name]
    
    def drop_database(self, db_name):
        return self.client.drop_database(db_name)
    
    def get_item_by_id(self, db_name, item_id):
        db = self.client["db_model"]
        collection = db[db_name]
        try:
            # Ensure item_id is an ObjectId
            item = collection.find_one({"_id": item_id})
            if item:
                print("Item found:", item)
                return item
            else:
                print("Item not found")
                return None
        except Exception as e:
            print("Error:", e)
            return None


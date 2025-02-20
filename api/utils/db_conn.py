from pymongo import MongoClient

class MongoDBConn:
    def __init__(self, host='mongo', port=27017, username='root', password='root', authSource='admin'):
        
        self.client = MongoClient(
            f'mongodb://{username}:{password}@{host}:{port}/?authSource={authSource}'
        )
        
    def insert_data(self, db_name: str, df):
        db = self.client["db_model"]
        db_collect = db[db_name]
        df['_id'] = df['page'] 
        data = df.to_dict(orient='records')
        db_collect.insert_many(data)
    
    def get_item_by_id(self,db_name,item_id):
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
        
    def get_titles_by_item_ids(self, item_ids_list:list, db_name:str="full_items")->list:
        """
        Given a list item_ids_list, get the respective titles from database "db".
        """
        recommendation = []
        for item_id in item_ids_list:
            item = self.get_item_by_id(db_name,item_id)
            recommendation.append(item['title'])
        return recommendation


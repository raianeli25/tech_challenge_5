from utils.db_conn import MongoDBConn

db = MongoDBConn()

def get_titles_from_ids(item_ids_list:list, db_name:str="full_items")->list:
    """
    Given a list item_ids_list, get the respective titles from database "db".
    """
    recommendation = []
    for item_id in item_ids_list:
        item = db.get_item_by_id(db_name,item_id)
        recommendation.append(item['title'])
    return recommendation
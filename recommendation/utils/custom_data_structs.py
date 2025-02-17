class UserItemData():
    def __init__(self, 
                 user_id_map:dict = None, 
                 item_id_map:dict = None, 
                 user_id_map_reverse:dict = None, 
                 item_id_map_reverse:dict = None,
                 user_feature_map:dict = None,
                 item_feature_map:dict = None,
                 interactions_shape:tuple = None):
        self.user_id_map = user_id_map 
        self.item_id_map = item_id_map 
        self.user_id_map_reverse = user_id_map_reverse
        self.item_id_map_reverse = item_id_map_reverse
        self.user_feature_map = user_feature_map
        self.item_feature_map = item_feature_map
        self.interactions_shape = interactions_shape
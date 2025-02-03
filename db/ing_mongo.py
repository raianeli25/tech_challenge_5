import pandas as pd
from pymongo import MongoClient

df_movies = pd.read_csv('../pipeline/movies.csv', 
    sep='\t', 
    encoding='latin-1', 
    usecols=['movie_id', 'title', 'genres']
)
df_ratings = pd.read_csv('../pipeline/ratings.csv', 
    sep='\t', 
    encoding='latin-1', 
    usecols=['user_id', 'movie_id', 'rating', 'timestamp']
)

client = MongoClient("mongodb://root:root@mongo:27017/")
db = client["movie_database"]

movies_collection = db["movies"]
movies_data = df_movies.to_dict(orient='records')
movies_collection.insert_many(movies_data)

ratings_collection = db["ratings"]
ratings_data = df_ratings.to_dict(orient='records')
ratings_collection.insert_many(ratings_data)

print("Data inserted successfully!")


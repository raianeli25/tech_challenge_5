import os

from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()
client = MongoClient()

@app.get('/')
def route_default():
    return 'Welcome to API'

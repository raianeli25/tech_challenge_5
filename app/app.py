import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL")

def default():
    st.button('teste')

default()
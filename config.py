import streamlit as st

API_KEY = st.secrets["api"]["key"]
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY
}

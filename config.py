import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY
}

import requests
from config import Config

URL = "http://127.0.0.1:8000/api/raw_data/"
params = {
    "db_name": Config.MONGO_DB_NAME,
    "collection_name": Config.MONGO_COLLECTION,
    "skip": 0,
    "limit": 5,
}
response = requests.get(URL, params=params)
print(response.status_code, response.json())

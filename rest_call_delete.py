import requests
from config import Config

URL_DELETE = "http://127.0.0.1:8000/api/delete_mongodb/"

try:
    response = requests.delete(
        URL_DELETE,
        params={
            "db_name": Config.MONGO_DB_NAME,
            "collection_name": Config.MONGO_COLLECTION,
        },
    )
    print(response.json())
except Exception as e:
    print(f"Error decoding response: {e}")
    print(f"Raw response text: {response.text}")

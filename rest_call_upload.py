import requests

URL_UPLOAD = "http://127.0.0.1:8000/api/upload/"
FILE_PATH = "data/housing.csv"

with open(FILE_PATH, "rb") as file:
    files = {"file": file}
    response = requests.post(URL_UPLOAD, files=files)
    try:
        print(response.json())
    except Exception as e:
        print(f"Error decoding response: {e}")
        print(f"Raw response text: {response.text}")

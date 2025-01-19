import requests

URL = "http://127.0.0.1:8000/api/health/"
response = requests.get(URL)
print(response.status_code, response.json())

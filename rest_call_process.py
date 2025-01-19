import requests

# Endpoint URL
URL_PROCESS = "http://127.0.0.1:8000/api/process/"

try:
    # Make the GET request
    response = requests.get(URL_PROCESS)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"Error occurred: {e}")

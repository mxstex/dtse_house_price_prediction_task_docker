import requests

URL = "http://127.0.0.1:8000/api/predicted_data/"

try:
    response = requests.get(URL, params={"skip": 0, "limit": 10})
    print(f"Status Code: {response.status_code}")

    # Debug raw response content
    print(f"Raw Response: {response.content}")

    # Parse JSON response
    if response.status_code == 200:
        data = response.json()
        print(f"Predicted Data: {data.get('predicted_data', [])}")
    else:
        print(f"Error: {response.status_code}, {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")

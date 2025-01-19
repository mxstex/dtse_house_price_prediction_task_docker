from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)


@patch("routes.routes.MongoClient")
def test_health_endpoint(mock_mongo_client):
    print(f"Mock is active: {mock_mongo_client}")
    mock_client_instance = mock_mongo_client.return_value
    mock_client_instance.admin.command.return_value = {"ok": 1}

    response = client.get("/api/health")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch("routes.routes.MongoClient")
def test_process_endpoint(mock_mongo_client):
    mock_mongo_client.return_value["test_db"]["test_collection"].find.return_value = [
        {"feature1": 1, "feature2": 2, "feature3": 3}
    ]
    response = client.get(
        "/api/process",
        params={"db_name": "test_db", "collection_name": "test_collection"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Data processed and stored successfully in PostgreSQL."
    }


@patch("routes.routes.MongoClient")
def test_upload_endpoint(mock_mongo_client):
    mock_mongo_client.return_value["test_db"][
        "test_collection"
    ].insert_many.return_value = None
    response = client.post(
        "/api/upload",
        files={"file": ("test.csv", b"feature1,feature2,median_house_value\n1,2,3")},
        data={"db_name": "test_db", "collection_name": "test_collection"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Data uploaded and stored successfully."}


@patch("routes.routes.MongoClient")
def test_delete_endpoint(mock_mongo_client):
    mock_mongo_client.return_value["test_db"][
        "test_collection"
    ].delete_many.return_value.deleted_count = 1
    response = client.delete(
        "/api/delete_mongodb/",
        params={"db_name": "test_db", "collection_name": "test_collection"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "All documents in test_db.test_collection have been deleted successfully."
    }


def test_get_predicted_data():
    response = client.get("/api/predicted_data")
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    data = response.json()
    assert "predicted_data" in data, "Response missing 'predicted_data' field"
    assert isinstance(data["predicted_data"], list), "Predicted data is not a list"

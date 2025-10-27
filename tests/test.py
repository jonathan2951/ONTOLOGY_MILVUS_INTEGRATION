from fastapi.testclient import TestClient
from src.app import app
import pytest
from pymilvus import MilvusClient

client = TestClient(app)


# @pytest.fixture(scope="session")
# def milvus_client():
#     client = MilvusClient("http://localhost:19530")  # Use your connection string
#     yield client
#     client.close()


# test entry point
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "VectorDB semantic search API is running",
        "version": "1.0.0",
    }


# test milvus client
def test_readiness():
    response = client.get("/readiness")
    # response_json = response.json()
    # print(response_json)
    assert response.status_code == 200
    # assert response_json.get("status") == "ready"
    # assert response_json.get("milvus_version") == "2.6.4"
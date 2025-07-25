import pytest
import requests
import os
import time
import uuid

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5001")


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Waits for the API to be ready before running tests."""
    start_time = time.time()
    while time.time() - start_time < 30:
        try:
            response = requests.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                return
        except requests.ConnectionError:
            time.sleep(1)
    pytest.fail("API did not become available within 30 seconds.")


def create_unique_item_payload():
    unique_name = f"test-item-{uuid.uuid4()}"
    return {"name": unique_name, "description": "A test item"}


def test_get_all_items_initially_empty():
    response = requests.get(f"{API_BASE_URL}/items")
    assert response.status_code == 200
    assert response.json() == []


def test_post_item_and_get_it_back():
    payload = create_unique_item_payload()
    post_response = requests.post(f"{API_BASE_URL}/items", json=payload)
    assert post_response.status_code == 201
    created_item = post_response.json()
    assert "id" in created_item
    item_id = created_item["id"]

    get_response = requests.get(f"{API_BASE_URL}/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json() == created_item


def test_get_nonexistent_item():
    response = requests.get(f"{API_BASE_URL}/items/non-existent-id")
    assert response.status_code == 404


def test_duplicate_post_request():
    payload = {"name": f"duplicate-test-{uuid.uuid4()}", "description": "Testing duplicates"}
    response1 = requests.post(f"{API_BASE_URL}/items", json=payload)
    assert response1.status_code == 201

    response2 = requests.post(f"{API_BASE_URL}/items", json=payload)
    assert response2.status_code == 409


def test_put_update_item():
    payload = create_unique_item_payload()
    post_response = requests.post(f"{API_BASE_URL}/items", json=payload)
    assert post_response.status_code == 201
    item_id = post_response.json()["id"]

    update_payload = {"name": "Updated Name", "description": "Updated Description"}
    put_response = requests.put(f"{API_BASE_URL}/items/{item_id}", json=update_payload)
    assert put_response.status_code == 200
    updated_item = put_response.json()
    assert updated_item["name"] == "Updated Name"


def test_put_nonexistent_item():
    response = requests.put(f"{API_BASE_URL}/items/non-existent-id", json={"name": "Won't Work"})
    assert response.status_code == 404


def test_delete_item():
    payload = create_unique_item_payload()
    post_response = requests.post(f"{API_BASE_URL}/items", json=payload)
    assert post_response.status_code == 201
    item_id = post_response.json()["id"]

    delete_response = requests.delete(f"{API_BASE_URL}/items/{item_id}")
    assert delete_response.status_code == 200

    get_response = requests.get(f"{API_BASE_URL}/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_item():
    response = requests.delete(f"{API_BASE_URL}/items/non-existent-id")
    assert response.status_code == 404
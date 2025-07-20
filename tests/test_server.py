import pytest
from fastapi.testclient import TestClient

import os
import json

# We need to import the app from the server file
from src.server import app

# Create a test client
client = TestClient(app)

# Get the token from an environment variable for integration testing
spotify_token = os.environ.get("SPOTIFY_ACCESS_TOKEN")

@pytest.mark.skipif(not spotify_token, reason="SPOTIFY_ACCESS_TOKEN environment variable not set")
def test_agent_get_setlist_success():
    """
    Tests the /api/agent/setlist endpoint for a successful scenario.
    """
    response = client.post(
        "/api/agent/setlist",
        headers={"Authorization": f"Bearer {spotify_token}"},
        json={"artistName": "Radiohead"}  # Using a real artist
    )

    # Assertions for a real API call
    assert response.status_code == 200
    response_data = response.json()
    assert "songs" in response_data
    assert isinstance(response_data["songs"], list)


def test_agent_get_setlist_no_auth():
    """
    Tests that the endpoint returns a 401 Unauthorized if the token is missing.
    """
    response = client.post(
        "/api/agent/setlist",
        json={"artistName": "Test Band"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header missing"

def test_agent_get_setlist_no_artist():
    """
    Tests that the endpoint returns a 400 Bad Request if artistName is missing.
    """
    response = client.post(
        "/api/agent/setlist",
        headers={"Authorization": "Bearer fake-token"},
        json={} # Missing artistName
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing artistName in request body"
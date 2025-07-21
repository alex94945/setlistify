import pytest
from src.tools.spotify_tools import create_playlist
from src.auth.spotify_oauth import refresh_token
import os
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.

# This test requires a valid Spotify OAuth refresh token.
# It will be used to automatically fetch a fresh access token.
# Set the token in your .env file:
# SPOTIFY_REFRESH_TOKEN='your-real-refresh-token'

REFRESH_TOKEN = os.environ.get("SPOTIFY_REFRESH_TOKEN")

@pytest.mark.skipif(not REFRESH_TOKEN, reason="Spotify refresh token not found in environment variables")
def test_create_real_spotify_playlist():
    """Tests the creation of a Spotify playlist using the real Spotify API."""
    
    # 1. Get a fresh access token using the refresh token
    print("\nAttempting to refresh Spotify token...")
    token_data = refresh_token(REFRESH_TOKEN)
    assert "error" not in token_data, f"Failed to refresh token: {token_data.get('error')}"
    access_token = token_data.get("access_token")
    assert access_token, "Access token not found in refresh response."
    print("Successfully refreshed Spotify token.")

    # 2. Run the test with the new access token
    artist_name = "Metallica"
    tracks = [
        "For Whom the Bell Tolls",
        "Master of Puppets",
        "Enter Sandman",
        "One",
        "Fade to Black"
    ]

    event_date = "2025-01-01"
    venue_name = "Test Venue"
    result = create_playlist(access_token, artist_name, tracks, event_date, venue_name)

    assert "error" not in result, f"API call failed with error: {result.get('error')}"
    assert "playlist_url" in result
    assert isinstance(result["playlist_url"], str)
    assert "spotify.com/playlist/" in result["playlist_url"]
    assert result["songs_added"] == 5

import pytest
from src.tools.spotify_tools import create_playlist

@pytest.mark.skip(reason="Skipping until a mock or real access token is available")
def test_create_spotify_playlist():
    # This test requires a valid Spotify OAuth access token.
    # You can obtain one by following the Spotify Authorization Guide.
    # https://developer.spotify.com/documentation/web-api/tutorials/code-flow
    access_token = "YOUR_ACCESS_TOKEN"
    playlist_name = "Test Playlist"
    tracks = ["Bohemian Rhapsody - Queen", "Stairway to Heaven - Led Zeppelin"]

    playlist_url = create_spotify_playlist(access_token, playlist_name, tracks)

    assert isinstance(playlist_url, str)
    assert "spotify.com/playlist/" in playlist_url

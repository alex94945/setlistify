from smolagents import tool
import requests

@tool
def create_spotify_playlist(access_token: str, name: str, tracks: list[str]) -> str:
    """
    Create a Spotify playlist and return its public URL.

    Args:
        access_token (str): User-specific OAuth token with playlist-modify scope
        name (str): Playlist title
        tracks (list[str]): Track names (must include artist in search step)

    Returns:
        str: URL of the newly-created playlist.
    """
    base = "https://api.spotify.com/v1"
    hdr = {"Authorization": f"Bearer {access_token}"}

    # 1) who is the user?
    user_id = requests.get(f"{base}/me", headers=hdr, timeout=10).json()["id"]

    # 2) create empty playlist
    pl = requests.post(
        f"{base}/users/{user_id}/playlists",
        json={"name": name, "public": True},
        headers=hdr, timeout=10
    ).json()
    playlist_id = pl["id"]

    # 3) search each song → URI
    uris = []
    for title in tracks:
        q = requests.get(
            f"{base}/search",
            params={"q": title, "type": "track", "limit": 1},
            headers=hdr, timeout=10
        ).json()
        items = q.get("tracks", {}).get("items", [])
        if items:
            uris.append(items[0]["uri"])

    # 4) add them (Spotify allows 100/req)
    if uris:
        requests.post(
            f"{base}/playlists/{playlist_id}/tracks",
            json={"uris": uris},
            headers=hdr, timeout=10
        )

    return pl["external_urls"]["spotify"]

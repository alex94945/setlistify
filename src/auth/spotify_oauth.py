import os, time, requests
from urllib.parse import urlencode

AUTH_URL  = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPES = "playlist-modify-public playlist-modify-private"

def auth_url(state: str) -> str:
    params = dict(response_type="code", client_id=CLIENT_ID,
                  redirect_uri=REDIRECT_URI, scope=SCOPES, state=state)
    return f"{AUTH_URL}?{urlencode(params)}"

def exchange_code(code: str) -> dict:
    resp = requests.post(TOKEN_URL, data=dict(
        grant_type="authorization_code",
        code=code,
        redirect_uri=REDIRECT_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ), timeout=10)
    resp.raise_for_status()
    data = resp.json()
    data["expires_at"] = int(time.time()) + data["expires_in"]
    return data  # {access_token, refresh_token, expires_at}

def refresh_token(refresh_token: str) -> dict:
    resp = requests.post(TOKEN_URL, data=dict(
        grant_type="refresh_token",
        refresh_token=refresh_token,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ), timeout=10)
    resp.raise_for_status()
    data = resp.json()
    data["refresh_token"] = refresh_token  # Spotify omits it on refresh
    data["expires_at"] = int(time.time()) + data["expires_in"]
    return data

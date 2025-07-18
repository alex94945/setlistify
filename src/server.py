from fastapi import FastAPI, Request, HTTPException, Response, Depends
from .auth.spotify_oauth import auth_url, exchange_code, refresh_token
from .agent import build_agent
from .tools.setlist_tools import search_artist, get_latest_show
from .tools.spotify_tools import create_playlist
import spotipy
import secrets, json, time, redis.asyncio as redis

app = FastAPI(title="Setlistify")
rdb = redis.from_url("redis://localhost:6379")
agent = build_agent()


# ---------- session helpers ----------
async def load_tokens(sid: str):
    data = await rdb.get(f"sid:{sid}")
    if not data:
        raise HTTPException(401, "Session expired")
    return json.loads(data)

async def save_tokens(sid: str, tk: dict):
    await rdb.set(f"sid:{sid}", json.dumps(tk))

def require_sid(req: Request):
    sid = req.cookies.get("sid")
    if not sid:
        raise HTTPException(401, "Login first")
    return sid

# ---------- routes ----------
@app.get("/login")
def login():
    state = secrets.token_urlsafe(16)
    url = auth_url(state)
    resp = Response(status_code=302, headers={"Location": url})
    resp.set_cookie("oauth_state", state, max_age=600, httponly=True)
    return resp

@app.get("/callback")
async def callback(code: str, state: str, request: Request):
    if state != request.cookies.get("oauth_state"):
        raise HTTPException(400, "Bad state")
    tokens = exchange_code(code)
    sid = secrets.token_urlsafe(32)
    await save_tokens(sid, tokens)
    r = Response("✅ Spotify linked. Return to the app.")
    r.set_cookie("sid", sid, httponly=True, samesite="Lax")
    return r

@app.get("/api/searchArtist")
async def search_artist_route(q: str):
    if not q:
        raise HTTPException(400, "Query parameter 'q' is required")
    return search_artist(q)


@app.get("/api/setlist")
async def get_setlist_route(mbid: str, shows: int = 3):
    if not mbid:
        raise HTTPException(400, "Query parameter 'mbid' is required")
    # Note: get_latest_show uses artist name, but the logic inside first searches by name then uses mbid.
    # This is slightly inefficient but reuses the existing tool. For a real app, you might refactor
    # get_latest_show to accept an mbid directly.
    # For now, we'll just pass the mbid as the name, as the search will still resolve it.
    shows_data = get_latest_show(artist_name=mbid, count=shows)
    if not shows_data or "error" in shows_data[0]:
        error_msg = shows_data[0].get("error", "Failed to get setlist") if shows_data else "Unknown error"
        raise HTTPException(500, error_msg)
    
    # As per the plan, we need to return a list of songs and some metadata.
    all_songs = [song for show in shows_data for song in show.get("setlist", [])]
    deduped_songs = list(dict.fromkeys(all_songs)) # Simple de-dupe preserving order

    shows_meta = [
        {
            "date": show.get("event_date"),
            "venue": show.get("venue"),
            "city": show.get("city"),
        }
        for show in shows_data
    ]

    return {"songs": deduped_songs[:50], "showsMeta": shows_meta}


@app.post("/api/createPlaylist")
async def create_playlist_route(req: Request, sid=Depends(require_sid)):
    body = await req.json()
    artist_name = body.get("artistName")
    songs = body.get("songs")

    if not artist_name or not songs:
        raise HTTPException(400, "Missing artistName or songs in request body")

    tokens = await load_tokens(sid)
    if not tokens:
        raise HTTPException(401, "User not authenticated with Spotify")

    # Check if token needs refresh
    if tokens.get("expires_at", 0) < time.time():
        new_tokens = await refresh_token(tokens["refresh_token"])
        if "error" in new_tokens:
            raise HTTPException(500, "Failed to refresh Spotify token")
        await save_tokens(sid, new_tokens)
        tokens = new_tokens

    sp = spotipy.Spotify(auth=tokens["access_token"])
    user_id = sp.me()["id"]

    result = create_playlist(sp, user_id, artist_name, songs)

    if "error" in result:
        raise HTTPException(500, result["error"])

    return result


@app.post("/chat")
async def chat(req: Request, body: dict, sid=Depends(require_sid)):
    tokens = await load_tokens(sid)
    if tokens["expires_at"] < time.time():
        tokens = refresh_token(tokens["refresh_token"])
        await save_tokens(sid, tokens)

    # Pass token into agent’s memory ◀️ easiest: stash in user_message.meta
    body["meta"] = {"spotify_token": tokens["access_token"]}
    reply = agent(body["message"], meta=body.get("meta"))
    return reply

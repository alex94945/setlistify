from fastapi import FastAPI, Request, HTTPException, Response, Depends, Header
from .agent import build_agent_for_token
from .tools.setlist_tools import search_artist
from .tools.spotify_tools import create_playlist
import spotipy
import time
from typing import Annotated

app = FastAPI(title="Setlistify")

# ---------- Auth Dependency ----------
async def get_spotify_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    return parts[1]

@app.get("/api/searchArtist")
async def search_artist_route(q: str):
    if not q:
        raise HTTPException(400, "Query parameter 'q' is required")
    return search_artist(q)

@app.post("/api/agent/setlist")
async def agent_get_setlist(req: Request, token: str = Depends(get_spotify_token)):
    body = await req.json()
    artist_name = body.get("artistName")
    if not artist_name:
        raise HTTPException(400, "Missing artistName in request body")

    # Build a new agent for each request, with the user's token bound to the tool
    agent = build_agent_for_token(token=token)
    response = agent(f"create a playlist for {artist_name}")
    return response



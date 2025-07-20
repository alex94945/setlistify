from fastapi import FastAPI, Request, HTTPException, Response, Depends, Header
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from .agent import build_agent_for_token, trace_provider
from .tools.setlist_tools import search_artist
from .tools.spotify_tools import create_playlist
import spotipy
import json
import time
from typing import Annotated

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic can go here
    yield
    # Shutdown logic
    print("Shutting down OpenTelemetry tracer provider...")
    trace_provider.shutdown()
    print("Tracer provider shut down.")

app = FastAPI(title="Setlistify", lifespan=lifespan)

# Instrument the FastAPI app to automatically create traces for requests
FastAPIInstrumentor.instrument_app(app)

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

    # Add artist name to the current trace for better observability
    span = trace.get_current_span()
    span.set_attribute("artist.name", artist_name)

    # Build a new agent for each request, with the user's token bound to the tool
    agent = build_agent_for_token(token=token)
    response = agent(f"create a playlist for {artist_name}")
    
    # Add the final agent output to the trace
    span.set_attribute("llm.output", json.dumps(response))
    return response

@app.post("/api/external/createPlaylist")
async def create_playlist_route(req: Request, token: str = Depends(get_spotify_token)):
    body = await req.json()
    artist_name = body.get("artistName")
    songs = body.get("songs")
    if not artist_name or not songs:
        raise HTTPException(400, "Missing artistName or songs in request body")
    result = create_playlist(token, artist_name, songs)
    return result



from fastapi import FastAPI, Request, HTTPException, Response, Depends, Header
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from .agent import build_agent_for_token, trace_provider
from .tools.setlist_tools import search_artist
from .tools.spotify_tools import create_playlist
from .auth import spotify_oauth
from fastapi.responses import RedirectResponse
import spotipy
import json
import time
import uuid
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

tracer = trace.get_tracer("setlistify.server")

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

    with tracer.start_as_current_span("setlistify-agent-run") as span:
        # Add artist name and other metadata to the trace for better observability
        span.set_attribute("artist.name", artist_name)
        span.set_attribute("langfuse.tags", ["agent", "setlist"])
        # In a real app, you might get a user ID from the session
        span.set_attribute("langfuse.user_id", "anonymous")

        # Build a new agent for each request, with the user's token bound to the tool
        agent = build_agent_for_token(token=token)
        response = agent(f"create a playlist for {artist_name}")
        
        # Add the final agent output to the trace
        span.set_attribute("llm.output", json.dumps(response))
        return response

@app.post("/api/external/createPlaylist")
async def create_playlist_route(req: Request):
    body = await req.json()
    artist_name = body.get("artistName")
    songs = body.get("songs")
    event_date = body.get("eventDate")
    venue_name = body.get("venueName")

    if not all([artist_name, songs, event_date, venue_name]):
        raise HTTPException(400, "Missing artistName, songs, eventDate, or venueName in request body")

    # The create_playlist tool now handles its own authentication via refresh token
    result = create_playlist(
        artist_name=artist_name, 
        songs=songs, 
        event_date=event_date, 
        venue_name=venue_name
    )
    return result

# ---------- Auth Routes ----------
@app.get("/api/auth/login/spotify", tags=["Authentication"])
async def spotify_login():
    """Redirects the user to Spotify to authorize the application."""
    # Using a static state for simplicity in this context, 
    # but a dynamic, session-based state is recommended for production.
    state = "setlistify_auth_state"
    return RedirectResponse(spotify_oauth.auth_url(state))

@app.get("/api/auth/callback/spotify", tags=["Authentication"])
async def spotify_callback(code: str, state: str):
    """Handles the callback from Spotify after user authorization."""
    # In a production app, you should validate the 'state' parameter.
    if state != "setlistify_auth_state":
        raise HTTPException(status_code=400, detail="State mismatch error.")
    
    try:
        token_data = spotify_oauth.exchange_code(code)
        # For this tool, we return the token directly for the user to copy.
        # In a real app, you would establish a user session here.
        return token_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to exchange code for token: {e}")

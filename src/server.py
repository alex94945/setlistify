import json
import secrets
import toml
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import BaseModel
from spotipy import Spotify
from spotipy.cache_handler import CacheHandler
from spotipy.oauth2 import SpotifyOAuth

from .agent import build_agent_for_spotify_client, trace_provider

# Load configuration from toml file
config = toml.load("./config.toml")

# Set up OpenTelemetry
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("\nFlushing and shutting down OpenTelemetry tracer provider...")
    trace_provider.force_flush()
    trace_provider.shutdown()
    print("Tracer provider shut down.")

app = FastAPI(title="Setlistify", lifespan=lifespan)

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Allow both localhost and 127.0.0.1
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
tracer = trace.get_tracer("setlistify.server")
FastAPIInstrumentor.instrument_app(app, tracer_provider=trace_provider)

# --- Spotify OAuth2 and Session Management ---

# A simple dictionary to act as a server-side session store.
# In a production app, you would use a more robust solution like Redis.
sessions = dict()

class FastAPICacheHandler(CacheHandler):
    """
    A cache handler that stores tokens in our server-side session dictionary
    and applies a session cookie to the response.
    """
    def __init__(self, request: Request, response: Response = None):
        self.request = request
        self.response = response

    def get_cached_token(self):
        return sessions.get(self.request.cookies.get("session"))

    def save_token_to_cache(self, token_info):
        session_id = secrets.token_urlsafe(64)
        sessions[session_id] = token_info
        # The SessionMiddleware is not working reliably across ports.
        # We will set the cookie manually to ensure it has the correct domain.
        # self.request.session["token_info"] = token_info

        # Manually set the cookie on the response object passed to the handler
        if self.response:
            self.response.set_cookie(
                key="session", 
                value=session_id, 
                domain="127.0.0.1",
                httponly=True,
                samesite='lax' # Use 'lax' for cross-origin redirects
            )

def get_spotify_client(cache_handler=Depends(FastAPICacheHandler)) -> Spotify:
    """
    FastAPI dependency to get a Spotipy client. It handles the auth flow.

    If the user is not authenticated, it raises a 401 HTTPException with the
    Spotify authorization URL. The frontend should handle this by redirecting
    the user to this URL.
    """
    auth_manager = SpotifyOAuth(**config["spotipy"], cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        raise HTTPException(status_code=401, detail=auth_url)
    return Spotify(auth_manager=auth_manager)

@app.get("/auth")
def spotify_auth(cache_handler=Depends(FastAPICacheHandler)):
    """
    Initiate Spotify OAuth flow by redirecting to Spotify's authorization URL.
    """
    auth_manager = SpotifyOAuth(**config["spotipy"], cache_handler=cache_handler)
    auth_url = auth_manager.get_authorize_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/status")
def auth_status(cache_handler=Depends(FastAPICacheHandler)):
    """
    Check if user is authenticated and return profile info if logged in.
    """
    auth_manager = SpotifyOAuth(**config["spotipy"], cache_handler=cache_handler)
    token_info = cache_handler.get_cached_token()
    
    if not auth_manager.validate_token(token_info):
        return {"authenticated": False}
    
    try:
        spotify = Spotify(auth_manager=auth_manager)
        user_info = spotify.current_user()
        return {
            "authenticated": True,
            "user": {
                "name": user_info.get("display_name", "Spotify User"),
                "image": user_info.get("images", [{}])[0].get("url") if user_info.get("images") else None,
                "id": user_info.get("id")
            }
        }
    except Exception:
        return {"authenticated": False}

@app.get("/callback")
def spotify_callback(code: str, response: Response, cache_handler=Depends(FastAPICacheHandler)):
    """
    Callback endpoint for Spotify to redirect to after user authorization.
    """
    # The cache handler needs access to the response object to set the session cookie
    cache_handler.response = response

    # The auth_manager will get the token and use the cache handler to save it
    auth_manager = SpotifyOAuth(**config["spotipy"], cache_handler=cache_handler)
    auth_manager.get_access_token(code, as_dict=False)

    # The cookie is now set on the response object. Now, configure the redirect.
    response.status_code = 307  # Temporary Redirect
    response.headers["Location"] = "http://127.0.0.1:3000/"
    return response

@app.get("/logout")
def logout(request: Request):
    """Clear the server-side session."""
    session_id = request.cookies.get("session")
    if session_id in sessions:
        del sessions[session_id]
    return {"detail": "Logged out successfully."}


# --- API Routes ---

class SetlistRequest(BaseModel):
    artistName: str

@app.get("/api/agent/setlist")
def get_setlist_stream(artistName: str, spotify_client=Depends(get_spotify_client)):
    """Stream agent progress updates while generating setlist"""
    artist_name = artistName
    
    def generate_progress():
        import time
        import json
        
        try:
            # Send initial progress
            yield f"data: {json.dumps({'type': 'progress', 'message': f'🎵 Searching for {artist_name} setlists...', 'step': 1, 'total': 5})}\n\n"
            time.sleep(1)
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '🔍 Analyzing recent concerts and tours...', 'step': 2, 'total': 5})}\n\n"
            time.sleep(2)
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '🎸 Compiling the ultimate setlist...', 'step': 3, 'total': 5})}\n\n"
            time.sleep(1)
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '🎧 Matching songs to Spotify tracks...', 'step': 4, 'total': 5})}\n\n"
            
            # Actually run the agent
            with tracer.start_as_current_span("agent.setlist") as span:
                span.set_attribute("langfuse.tags", ["agent", "setlist"])
                user_id = spotify_client.me()["id"]
                span.set_attribute("langfuse.user_id", user_id)
                
                agent = build_agent_for_spotify_client(spotify_client=spotify_client)
                response = agent(f"create a playlist for {artist_name}")
                
                span.set_attribute("llm.output", json.dumps(response))
            
            yield f"data: {json.dumps({'type': 'progress', 'message': '✨ Finalizing your playlist...', 'step': 5, 'total': 5})}\n\n"
            time.sleep(1)
            
            # Send final result
            yield f"data: {json.dumps({'type': 'complete', 'data': response})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

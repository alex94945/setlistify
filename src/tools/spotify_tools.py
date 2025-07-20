import spotipy
from smolagents import tool
import os
from dotenv import load_dotenv
from datetime import datetime
from src.auth.spotify_oauth import refresh_token

load_dotenv()

@tool
def create_playlist(artist_name: str, songs: list[str], event_date: str, venue_name: str) -> dict:
    """Creates a Spotify playlist for the given user with the given songs, including event details in the name.

    Args:
        artist_name (str): The name of the artist.
        songs (list[str]): A list of song titles to add to the playlist.
        event_date (str): The date of the event (format DD-MM-YYYY).
        venue_name (str): The name of the venue.
    """
    # 1. Get a fresh access token using the refresh token
    refresh_token_val = os.environ.get("SPOTIFY_REFRESH_TOKEN")
    if not refresh_token_val:
        return {"error": "Spotify refresh token not found in environment variables."}

    token_data = refresh_token(refresh_token_val)
    if "error" in token_data:
        return {"error": f"Failed to refresh token: {token_data.get('error')}"}
    access_token = token_data.get("access_token")
    if not access_token:
        return {"error": "Access token not found in refresh response."}

    # 2. Format the playlist name
    try:
        formatted_date = datetime.strptime(event_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        playlist_name = f"{artist_name} at {venue_name} ({formatted_date})"
    except ValueError:
        # Fallback if date format is unexpected
        playlist_name = f"{artist_name} at {venue_name} on {event_date}"
    
    playlist_description = f"A playlist generated from the setlist of {artist_name} at {venue_name} on {event_date}. Created by Setlistify."

    try:
        sp = spotipy.Spotify(auth=access_token)
        user_id = sp.me()["id"]

        # 3. Create the playlist
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=playlist_description
        )
        playlist_id = playlist['id']
        playlist_url = playlist['external_urls']['spotify']

        # 4. Search for tracks on Spotify
        track_uris = []
        for song in songs:
            # First, try to find the song by the specified artist
            query_by_artist = f'track:"{song}" artist:"{artist_name}"'
            results = sp.search(q=query_by_artist, type='track', limit=1)

            # If not found, it might be a cover. Search for the track by any artist.
            if not results['tracks']['items']:
                print(f"Could not find '{song}' by '{artist_name}'. Searching for it as a potential cover.")
                query_any_artist = f'track:"{song}"'
                results = sp.search(q=query_any_artist, type='track', limit=1)

            if results['tracks']['items']:
                track_uris.append(results['tracks']['items'][0]['uri'])
            else:
                print(f"Could not find track '{song}' on Spotify at all.")

        # 5. Add tracks to the playlist
        if track_uris:
            sp.playlist_add_items(playlist_id, track_uris)

        return {"playlist_url": playlist_url, "playlist_name": playlist_name, "songs_added": len(track_uris)}

    except spotipy.SpotifyException as e:
        return {"error": f"Spotify API error: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"} 

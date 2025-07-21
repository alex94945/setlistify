import spotipy
from smolagents import tool
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

@tool
def create_playlist(spotify_client: spotipy.Spotify, artist_name: str, songs: list[str], event_date: str, venue_name: str) -> dict:
    """Creates a Spotify playlist with a given list of songs.

    Args:
        spotify_client (spotipy.Spotify): An authenticated Spotify client.
        artist_name (str): The name of the artist.
        songs (list[str]): A list of song titles to add to the playlist.
        event_date (str): The date of the event (e.g., '2025-07-05').
        venue_name (str): The name of the venue.

    Returns:
        dict: A dictionary containing the playlist URL, name, and number of songs added.
    """
    try:
        user_id = spotify_client.current_user()["id"]

        # Format the playlist name
        try:
            # Assuming event_date is in a format like 'YYYY-MM-DD'
            formatted_date = datetime.strptime(event_date, "%Y-%m-%d").strftime("%b %d, %Y")
            playlist_name = f"{artist_name} at {venue_name} - {formatted_date}"
        except ValueError:
            # Fallback if date format is unexpected
            playlist_name = f"{artist_name} at {venue_name} on {event_date}"

        playlist = spotify_client.user_playlist_create(user_id, playlist_name, public=True)
        playlist_url = playlist["external_urls"]["spotify"]

        track_uris = []
        songs_added_titles = []
        for song in songs:
            # Search first with artist and song
            results = spotify_client.search(q=f"artist:{artist_name} track:{song}", type="track", limit=1)
            tracks = results["tracks"]["items"]
            if tracks:
                track_uris.append(tracks[0]["uri"])
                songs_added_titles.append(tracks[0]["name"])
            else:
                # If no results, search just by song title (for covers, etc.)
                results = spotify_client.search(q=f"track:{song}", type="track", limit=1)
                tracks = results["tracks"]["items"]
                if tracks:
                    track_uris.append(tracks[0]["uri"])
                    songs_added_titles.append(tracks[0]["name"])

        if track_uris:
            spotify_client.playlist_add_items(playlist["id"], track_uris)

        return {
            "playlist_url": playlist_url,
            "playlist_name": playlist_name,
            "songs_added": len(track_uris),
            "song_titles": songs_added_titles
        }
    except spotipy.SpotifyException as e:
        # Catch specific Spotify API errors for better feedback
        print(f"Spotify API Error: {e}")
        return {"error": f"Spotify API Error: {e.reason}"}
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred while creating the playlist."}

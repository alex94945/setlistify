from smolagents import tool

import os
import requests
import time
from smolagents import tool

SETLISTFM_API_KEY = os.getenv("SETLISTFM_API_KEY")

@tool
def get_latest_setlist(artist_name: str, count: int = 1) -> list:
    """
    Fetches the latest `count` setlists for the given artist name using setlist.fm API.

    Args:
        artist_name (str): The name of the artist to search for.
        count (int, optional): How many of the latest setlists to retrieve. Defaults to 1.

    Returns:
        list: A list of dicts, each containing setlist info.
    """
    # Step 1: Find artist MBID
    search_url = f"https://api.setlist.fm/rest/1.0/search/artists?artistName={artist_name}&p=1&sort=relevance"
    headers = {
        "x-api-key": SETLISTFM_API_KEY,
        "Accept": "application/json"
    }
    time.sleep(0.6)
    resp = requests.get(search_url, headers=headers)
    resp.raise_for_status()
    results = resp.json()
    if not results.get("artist"):
        return [{"error": f"Artist '{artist_name}' not found."}]
    artist = results["artist"][0]
    mbid = artist["mbid"]
    
    # Step 2: Get latest setlists
    setlist_url = f"https://api.setlist.fm/rest/1.0/artist/{mbid}/setlists?p=1"
    time.sleep(0.6)
    resp = requests.get(setlist_url, headers=headers)
    resp.raise_for_status()
    setlists = resp.json().get("setlist", [])
    # print("Raw setlists JSON:", setlists)
    if not setlists:
        return [{"error": f"No setlists found for artist '{artist_name}'."}]
    # Limit to the requested count
    setlists = setlists[:count]
    result = []
    for latest in setlists:
        info = {
            "artist": artist.get("name"),
            "event_date": latest.get("eventDate"),
            "venue": latest.get("venue", {}).get("name"),
            "city": latest.get("venue", {}).get("city", {}).get("name"),
            "country": latest.get("venue", {}).get("city", {}).get("country", {}).get("name"),
            "url": latest.get("url"),
            # Collect all song names from all sets (main set, encores, etc), skipping None values
            "setlist": [
                song.get("name")
                for set_block in latest.get("sets", {}).get("set", [])
                for song in set_block.get("song", [])
                if song.get("name")
            ],
        }
        result.append(info)
    return result


# @tool
# def dedupe_songlist():
#     pass

# @tool
# def create_spotify_playlist():
#     pass

from smolagents import tool

import os
import requests
import time

SETLISTFM_API_KEY = os.getenv("SETLISTFM_API_KEY")
SPOTIFY_API_KEY = os.getenv("SPOTIFY_API_KEY")


@tool
def search_artist(artist_name: str) -> list:
    """
    Searches for an artist by name using the setlist.fm API.

    Args:
        artist_name (str): The name of the artist to search for.

    Returns:
        list: A list of artist dictionaries, each containing name, mbid, and disambiguation.
    """
    search_url = f"https://api.setlist.fm/rest/1.0/search/artists?artistName={artist_name}&p=1&sort=relevance"
    headers = {"x-api-key": SETLISTFM_API_KEY, "Accept": "application/json"}
    try:
        time.sleep(0.6)  # Respect rate limits
        resp = requests.get(search_url, headers=headers)
        resp.raise_for_status()
        results = resp.json().get("artist", [])
        return [
            {
                "name": artist.get("name"),
                "mbid": artist.get("mbid"),
                "disambiguation": artist.get("disambiguation"),
            }
            for artist in results
        ]
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch artist '{artist_name}': {e}")
        return [{"error": str(e)}]


@tool
def get_latest_show(artist_name: str, count: int = 1) -> list:
    """
    Fetches the latest `count` shows for the given artist name using setlist.fm API.

    Args:
        artist_name (str): The name of the artist to search for.
        count (int, optional): How many of the latest shows to retrieve. Defaults to 1.

    Returns:
        list: A list of dicts, each containing show info, including the setlist.
    """
    # Step 1: Find artist MBID
    artists = search_artist(artist_name)
    if not artists or "error" in artists[0]:
        return artists  # Return error from search_artist
    artist = artists[0]
    mbid = artist["mbid"]
    
    # Step 2: Get latest shows
    shows_url = f"https://api.setlist.fm/rest/1.0/artist/{mbid}/setlists?p=1"
    resp = None
    for attempt in range(3):
        try:
            time.sleep(0.6)  # Keep original sleep to respect rate limits
            resp = requests.get(shows_url, headers=headers)
            resp.raise_for_status()
            break  # Break the loop if the request is successful
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for show search: {e}")
            if attempt < 2:
                time.sleep(1)  # Wait for 1 second before retrying
            else:
                return [{"error": f"Failed to fetch shows after 3 attempts: {e}"}]
    if resp is None: # Should not happen, but as a safeguard
        return [{"error": "Failed to get a response from show search."}]
    shows = resp.json().get("setlist", [])
    # print("Raw shows JSON:", shows)
    if not shows:
        return [{"error": f"No shows found for artist '{artist_name}'."}]
    # Limit to the requested count
    shows = shows[:count]
    result = []
    for show in shows:
        info = {
            "artist": artist.get("name"),
            "event_date": show.get("eventDate"),
            "venue": show.get("venue", {}).get("name"),
            "city": show.get("venue", {}).get("city", {}).get("name"),
            "country": show.get("venue", {}).get("city", {}).get("country", {}).get("name"),
            "url": show.get("url"),
            # Collect all song names from all sets (main set, encores, etc), skipping None values
            "setlist": [
                song.get("name")
                for set_block in show.get("sets", {}).get("set", [])
                for song in set_block.get("song", [])
                if song.get("name")
            ],
        }
        result.append(info)
    return result


@tool
def extract_setlist(shows: list) -> list:
    """
    Extracts a de-duplicated list of songs from a list of shows.

    Args:
        shows (list): A list of show dicts, from `get_latest_show`.

    Returns:
        list: A de-duplicated list of all songs from all shows.
    """
    all_songs = []
    for show in shows:
        all_songs.extend(show.get("setlist", []))
    # De-duplicate while preserving order
    return list(dict.fromkeys(all_songs))

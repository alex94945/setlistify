import spotipy

def create_playlist(sp: spotipy.Spotify, user_id: str, artist_name: str, songs: list[str]):
    """Creates a Spotify playlist for the given user with the given songs."""
    playlist_name = f"{artist_name} Setlist"
    playlist_description = f"A playlist generated from recent setlists of {artist_name}. Created by Setlistify."

    try:
        # 1. Create the playlist
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=playlist_description
        )
        playlist_id = playlist['id']
        playlist_url = playlist['external_urls']['spotify']

        # 2. Search for tracks on Spotify
        track_uris = []
        for song in songs:
            query = f"track:{song} artist:{artist_name}"
            results = sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track_uris.append(results['tracks']['items'][0]['uri'])

        # 3. Add tracks to the playlist
        if track_uris:
            sp.playlist_add_items(playlist_id, track_uris)

        return {"playlist_url": playlist_url, "playlist_name": playlist_name, "songs_added": len(track_uris)}

    except spotipy.exceptions.SpotifyException as e:
        return {"error": f"Spotify API error: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

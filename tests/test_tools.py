import os
import pytest
import src.config
import time

from src.tools import get_latest_setlist

# Make sure the SETLISTFM_API_KEY is set for the test environment
@pytest.mark.skipif(
    not os.getenv("SETLISTFM_API_KEY"),
    reason="SETLISTFM_API_KEY not set in environment"
)
def test_get_latest_setlist_basic():
    # Wait to comply with setlist.fm API rate limit (max 2/sec)
    time.sleep(0.6)
    # Use a well-known artist for a predictable result
    artist_name = "Metallica"
    result = get_latest_setlist(artist_name, count=1)
    print("Setlist result:", result)
    assert isinstance(result, list)
    assert len(result) == 1
    setlist = result[0]
    assert "artist" in setlist and setlist["artist"].lower() == "metallica"
    assert "setlist" in setlist and isinstance(setlist["setlist"], list)
    assert setlist["setlist"]  # Should not be empty
    assert "event_date" in setlist
    assert "venue" in setlist
    assert "city" in setlist
    assert "country" in setlist

def test_get_latest_setlist_multiple():
    # Wait to comply with setlist.fm API rate limit (max 2/sec)i
    time.sleep(0.6)
    artist_name = "Metallica"
    result = get_latest_setlist(artist_name, count=3)
    print("Setlists (3) result:", result)
    for i, setlist in enumerate(result):
        print(f"Setlist {i+1} URL:", setlist.get('url', '<no url>'))
    assert isinstance(result, list)
    assert len(result) == 3
    for setlist in result:
        assert "artist" in setlist and setlist["artist"].lower() == "metallica"
        assert "setlist" in setlist and isinstance(setlist["setlist"], list)
        assert setlist["setlist"]  # Should not be empty
        assert "event_date" in setlist
        assert "venue" in setlist
        assert "city" in setlist
        assert "country" in setlist

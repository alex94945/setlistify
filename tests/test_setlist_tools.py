import os
import pytest
import src.config
import time

from src.tools.setlist_tools import get_latest_show, extract_setlist

# Make sure the SETLISTFM_API_KEY is set for the test environment
@pytest.mark.skipif(
    not os.getenv("SETLISTFM_API_KEY"),
    reason="SETLISTFM_API_KEY not set in environment"
)
def test_get_latest_show_basic():
    # Wait to comply with setlist.fm API rate limit (max 2/sec)
    time.sleep(0.6)
    # Use a well-known artist for a predictable result
    artist_name = "Metallica"
    result = get_latest_show(artist_name, count=1)
    print("Show result:", result)
    assert isinstance(result, list)
    assert len(result) == 1
    show = result[0]
    assert "artist" in show and show["artist"].lower() == "metallica"
    assert "setlist" in show and isinstance(show["setlist"], list)
    assert show["setlist"]  # Should not be empty
    assert "event_date" in show
    assert "venue" in show
    assert "city" in show
    assert "country" in show

def test_get_latest_show_multiple():
    # Wait to comply with setlist.fm API rate limit (max 2/sec)i
    time.sleep(0.6)
    artist_name = "Metallica"
    result = get_latest_show(artist_name, count=3)
    print("Shows (3) result:", result)
    for i, show in enumerate(result):
        print(f"Show {i+1} URL:", show.get('url', '<no url>'))
    assert isinstance(result, list)
    assert len(result) == 3
    for show in result:
        assert "artist" in show and show["artist"].lower() == "metallica"
        assert "setlist" in show and isinstance(show["setlist"], list)
        assert show["setlist"]  # Should not be empty
        assert "event_date" in show
        assert "venue" in show
        assert "city" in show
        assert "country" in show

def test_extract_setlist():
    # Sample data mimicking the output of get_latest_show
    sample_shows = [
        {"setlist": ["Song A", "Song B", "Song C"]},
        {"setlist": ["Song B", "Song D", "Song E"]},
        {"setlist": ["Song A", "Song F"]},
        {"setlist": []} # a show with an empty setlist
    ]
    
    extracted_songs = extract_setlist(sample_shows)
    print("Extracted songs:", extracted_songs)
    
    # Check for de-duplication
    assert len(extracted_songs) == len(set(extracted_songs))
    
    # Check that all unique songs are present
    expected_songs = {"Song A", "Song B", "Song C", "Song D", "Song E", "Song F"}
    assert set(extracted_songs) == expected_songs

    # Test with empty input
    assert extract_setlist([]) == []

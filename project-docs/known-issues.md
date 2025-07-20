# **Setlistify — Known Issues**

This document lists known bugs, architectural inconsistencies, and potential issues found during a codebase review.

-   [ ] **Inefficient Agent Logic for Setlist Preview**
    -   **Files:** `src/server.py`, `src/prompts/system.md`, `setlistify-ui/components/steps/preview-setlist.tsx`
    -   **Root Cause:** The UI's "Preview Setlist" step calls the `/api/external/agent/setlist` endpoint, which invokes the full AI agent. The agent's prompt instructs it to find songs *and then* create a playlist. This is inefficient because the UI only needs the song list at this stage; the playlist creation happens in a later, separate step. The agent performs unnecessary planning and may even fail if it tries to call `create_playlist` prematurely.
    -   **Potential Fix:** Create a dedicated, non-agent FastAPI endpoint (e.g., `/api/setlist`) that directly calls the `get_latest_show` and `extract_setlist` tools. Update `preview-setlist.tsx` to call this new, more efficient endpoint. This will be faster, cheaper, and more reliable than invoking an LLM for a deterministic task.

-   [ ] **Mismatched API Route for Playlist Creation**
    -   **Files:** `src/server.py`, `setlistify-ui/components/steps/create-playlist.tsx`
    -   **Root Cause:** The `create-playlist.tsx` component attempts to `POST` to `/api/external/createPlaylist`. However, the FastAPI server defined in `src/server.py` does not have a `/api/createPlaylist` route. This will result in a 404 error.
    -   **Potential Fix:** Add a new endpoint to `src/server.py`, such as `@app.post("/api/createPlaylist")`, that accepts an artist name and a list of songs. This endpoint should directly call the `create_playlist` tool from `spotify_tools.py` using the provided user token.

-   [ ] **Artist Search Lacks Disambiguation**
    -   **Files:** `setlistify-ui/components/band-search-input.tsx`, `src/tools/setlist_tools.py`
    -   **Root Cause:** The UI plan specifies an autocomplete search to select a specific artist and their MusicBrainz ID (`mbid`). The current implementation uses a basic text input for the artist's name. The backend then has to search for the artist, taking the first result, which can be incorrect for artists with similar names (e.g., "Jeff Buckley" vs. "Jeff Williams"). This is inefficient and error-prone.
    -   **Potential Fix:** Enhance `band-search-input.tsx` to be an autocomplete component. As the user types, it should call the `/api/searchArtist` endpoint (which already exists in `src/server.py`). The user can then select the correct artist from a list. The chosen artist's `mbid` should be stored in the wizard's state and passed to the backend for subsequent calls, eliminating the need for further searches.

-   [x] **Incorrect Import in Server Tests**
    -   **File:** `tests/test_server.py`
    -   **Root Cause:** The test file `tests/test_server.py` contains the line `from src.server import app, build_agent`. The function `build_agent` does not exist in `src/server.py`; the correct function name is `build_agent_for_token` (located in `src/agent.py`). While `build_agent` is not used in the test, this incorrect import will cause the test suite to fail before any tests are run.
    -   **Potential Fix:** Correct the import statement in `tests/test_server.py` to `from src.server import app`.
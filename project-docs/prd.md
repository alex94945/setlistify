# **Setlistify — Product Requirements Document (PRD)**

## 1. Overview

**Product Name:** Setlistify

**Mission:** To instantly connect fans with the music from their favorite artists' live shows by transforming recent setlists into personal Spotify playlists.

**Target Audience:**
- Concert-goers who want to get hyped for an upcoming show by learning the songs.
- Fans who want to relive a recent concert experience.
- Music enthusiasts who want to discover what songs popular artists are have recently been playing live in preparation for the next show.

## 2. User Stories & Use Cases

| As a...        | I want to...                                                    | So that I can...                                                                |
| :------------- | :-------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| New Visitor    | Connect my Spotify account securely.                            | Authorize the app to create playlists in my library.                            |
| Music Fan      | Search for any artist by name.                                  | Find the artist I'm interested in.                                              |
| Music Fan      | See a list of songs from the artist's most recent shows.        | Preview the music and decide if I want to create a playlist.                    |
| Music Fan      | Create a new Spotify playlist from the setlist with one click.  | Save the songs to my library without manually searching for each one.            |
| Music Fan      | Get a direct link to open the newly created playlist.           | Immediately start listening to the playlist in my Spotify app.                  |
| Music Fan      | Start the process over again easily.                            | Create playlists for other artists without having to refresh or re-authenticate. |

## 3. Functional Requirements

### 3.1. Core Workflow (MVP)

1.  **Authentication:**
    - The user must be able to log in using their Spotify account via OAuth.
    - The application must request `playlist-modify-public` and `playlist-modify-private` scopes.
    - The user's session must be securely managed.

2.  **Artist Selection:**
    - The user must be able to input an artist's name.
    - The system will use this name to find the artist's latest setlists.

3.  **Setlist Preview:**
    - The system will fetch the most recent setlist(s) for the selected artist from the Setlist.fm API.
    - The system will display a de-duplicated list of songs from these setlists for the user to review.

4.  **Playlist Creation:**
    - The user must be able to trigger the creation of a new Spotify playlist.
    - The system will create a new, private playlist in the user's Spotify account named `[Artist Name] Setlist`.
    - The system will search for each song from the setlist on Spotify and add the corresponding tracks to the new playlist.

5.  **Confirmation & Access:**
    - The system will confirm that the playlist has been created successfully.
    - The system will provide a direct link for the user to open the new playlist in Spotify.

### 3.2. Technical Requirements

- **Backend:** An AI agent-powered service built with Python, FastAPI, and `smol-agents`.
- **Frontend:** A responsive, single-page web application built with Next.js and Tailwind CSS.
- **APIs:** Must integrate with Setlist.fm API (for setlists) and Spotify API (for auth and playlist creation).
- **Hosting:** The frontend and backend must be deployable on modern cloud platforms (e.g., Vercel, Fly.io).
- **Observability:** Agent interactions should be traced using LangFuse for debugging and monitoring.

## 4. Post-MVP

- **Multiple Show Merging:** Allow users to select how many recent shows (e.g., 1, 3, or 5) to merge into the playlist.
- **Autocomplete Search:** Implement a debounced search input that suggests artists as the user types, returning the artist's `mbid` to avoid ambiguity.
- **Playlist History:** Store a user's created playlists to be viewed later.
- **Dark Mode:** A UI toggle for a dark color scheme.
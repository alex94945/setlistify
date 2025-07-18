# src/agent.py
from smolagents import CodeAgent, PromptTemplates
from .llm import model             # Together AI wrapper
from .tools.setlist_tools import get_latest_show, extract_setlist, search_artist
from .tools.spotify_tools import create_playlist
from .tools.spotify import create_spotify_playlist

TOOLS = [get_latest_show, extract_setlist, create_playlist, create_spotify_playlist, search_artist]

from pathlib import Path

# Read the system prompt from the file
SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "system.md"
SYSTEM = SYSTEM_PROMPT_PATH.read_text()


def build_agent() -> CodeAgent:
    return CodeAgent(
        tools=TOOLS,
        model=model,
        # prompt_templates=PromptTemplates(system_prompt=SYSTEM),
        instructions=SYSTEM,
        name="Setlistify",
    )

# ---- Optional CLI entry point --------------------------------
if __name__ == "__main__":
    import argparse
    import json
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("--artist", required=True, help="Band name")
    parser.add_argument(
        "--token",
        required=False,
        help="Spotify user access-token. Is overridden by SPOTIFY_API_KEY env var.",
    )
    args = parser.parse_args()

    # Precedence: SPOTIFY_API_KEY > --token > prompt
    token = os.getenv("SPOTIFY_API_KEY") or args.token
    if not token:
        token = input("Please enter your Spotify access token: ")

    agent = build_agent()  # ← build with no meta
    resp = agent(  # ← pass meta at call time
        f"create playlist for {args.artist}", 
        context={"spotify_token": token}   # ← use context, not meta in smolagents >=1.20
    )

    print(json.dumps(resp, indent=2))


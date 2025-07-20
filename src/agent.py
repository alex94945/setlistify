# src/agent.py
import os
from pathlib import Path
import base64
from opentelemetry import trace
from smolagents import CodeAgent, OpenAIServerModel, tool

import logging
import sys

from .config import (
    LANGFUSE_HOST,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    TOGETHER_API_KEY,
)
from .tools.setlist_tools import extract_setlist, get_latest_show, search_artist
from .tools.spotify_tools import create_playlist
from opentelemetry.sdk.trace import TracerProvider
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OpenTelemetry to send traces to LangFuse
trace_provider = TracerProvider()
# Base64 encode credentials
credentials = f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

otlp_exporter = OTLPSpanExporter(
    endpoint=f"{LANGFUSE_HOST}/api/public/traces",
    headers={
        "Authorization": f"Basic {encoded_credentials}"
    }
)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Set the global tracer provider
trace.set_tracer_provider(trace_provider)

# Instrument smolagents
SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)

# Read the system prompt from the file
SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "system.md"
SYSTEM = SYSTEM_PROMPT_PATH.read_text()

model = OpenAIServerModel(
    model_id="deepseek-ai/DeepSeek-R1",
    api_base="https://api.together.xyz/v1",
    api_key=TOGETHER_API_KEY,
    timeout=60,
)

def build_agent_for_token(token: str) -> CodeAgent:
    """
    Return a CodeAgent whose `create_spotify_playlist`
    already knows the user's access-token.
    """

    @tool
    def create_playlist_for_user(artist_name: str, songs: list[str]) -> dict:
        """Securely creates a Spotify playlist using a pre-configured user token.

        This is a wrapper around the real `create_playlist` tool. It uses the
        access token provided when the agent was built, ensuring the secret
        token is never exposed to the language model.

        Args:
            artist_name (str): The name of the artist.
            songs (list[str]): A list of song titles to add to the playlist.
        """
        return create_playlist(access_token=token, artist_name=artist_name, songs=songs)

    # Overwrite the name to match what the LLM should see
    create_playlist_for_user.__name__ = "create_playlist"

    tools = [get_latest_show, extract_setlist, create_playlist_for_user, search_artist]

    return CodeAgent(
        tools=tools,
        model=model,
        instructions=SYSTEM,
        name="Setlistify",
    )


# ---- Optional CLI entry point --------------------------------
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--artist", required=True, help="Band name")
    parser.add_argument(
        "--token",
        required=False,
        help="Spotify user access-token. Is overridden by SPOTIFY_ACCESS_TOKEN env var.",
    )
    args = parser.parse_args()

    # Precedence: SPOTIFY_ACCESS_TOKEN > --token > prompt
    token = os.getenv("SPOTIFY_ACCESS_TOKEN") or args.token
    if not token:
        token = input("Please enter your Spotify access token: ")

    try:
        print("Building agent...")
        agent = build_agent_for_token(token=token)
        print("Agent built. Calling agent...")
        resp = agent(f"create playlist for {args.artist}")
        print("Agent call complete. Response:")
        # Also print the final output to the console, just in case.
        print(json.dumps(resp, indent=2))

    except Exception as e:
        print(f"An error occurred: {e}")

    print("\nFlushing and shutting down OpenTelemetry tracer provider...")
    trace_provider.force_flush()
    trace_provider.shutdown()
    print("Tracer provider shut down.")

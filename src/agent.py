# src/agent.py
import os
from pathlib import Path
import base64
from opentelemetry import trace
from smolagents import ToolCallingAgent, OpenAIServerModel, tool

import logging
import sys

from .config import (
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

tools = [get_latest_show, extract_setlist, create_playlist]

# This is the main, unauthenticated agent instance.
agent = ToolCallingAgent(
    tools=tools,
    model=model,
    instructions=SYSTEM,
    name="Setlistify",
    stream_outputs=True,
)

from spotipy import Spotify

def build_agent_for_spotify_client(spotify_client: Spotify) -> ToolCallingAgent:
    """
    Return a ToolCallingAgent whose `create_playlist` tool is already
    authenticated with a Spotify client.
    """

    @tool
    def create_playlist_for_user(artist_name: str, songs: list[str], event_date: str, venue_name: str) -> dict:
        """
        Creates a Spotify playlist for a given artist and set of songs.

        Args:
            artist_name: The name of the artist.
            songs: A list of song titles to add to the playlist.
            event_date: The date of the event (e.g., 'YYYY-MM-DD').
            venue_name: The name of the venue where the event took place.
        """
        return create_playlist(
            spotify_client=spotify_client,
            artist_name=artist_name,
            songs=songs,
            event_date=event_date,
            venue_name=venue_name,
        )

    authed_tools = [get_latest_show, extract_setlist, create_playlist_for_user]

    return ToolCallingAgent(
        tools=authed_tools,
        model=model,
        instructions=SYSTEM,
        name="Setlistify",
        stream_outputs=True,
    )

# ---- Optional CLI entry point --------------------------------
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--artist", required=True, help="The name of the artist")
    args = parser.parse_args()

    try:
        # The agent now handles authentication internally using the refresh token.
        # We just need to invoke it with the artist's name.
        final_answer = agent(f"Create a playlist for {args.artist}")
        print(f"Agent call complete. Response:\n{json.dumps(final_answer, indent=2)}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\nFlushing and shutting down OpenTelemetry tracer provider...")
        trace_provider.force_flush()
        trace_provider.shutdown()
        print("Tracer provider shut down.")

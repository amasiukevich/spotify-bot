from dotenv import load_dotenv

import os
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool

from livekit.plugins import (
    openai,
    cartesia,
    silero,
    # noise_cancellation,
    deepgram,
)

from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

from playing_script import player_client


@function_tool
def play_spotify_track(spotify_query: str):
    """
    Plays a song on Spotify.
    The spotify_query should be a string that represents the song to be played.
    Examples:
    - "Bohemian Rhapsody Queen"
    - "track:Doxy artist:Miles Davis".
    - "genre:jazz year:1960-1970"
    """
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="spotify_playback.log",  # Log to a file named spotify_playback.log
        filemode="a",  # Append to the file if it exists
    )

    logging.info(f"Spotify query: {spotify_query}")

    track_info = player_client.search_for_track_id(spotify_query, limit=1)
    player_client.start_playback(track_info[0]["id"])


@function_tool
def stop_playback():
    player_client.stop_current_playback()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            tools=[play_spotify_track, stop_playback],
            instructions="""
                You are a helpful assistant.
                Your only task is to produce queries to search for the spotify tracks.

                Example queries:
                - "genre:jazz year:1960-1970"
                - "Shape of You Ed Sheeran"
                - "track:Crazy Little Thing Called Love artist:Queen"

                You need to produce the queries to spotify based of what you receive from user.
                User speaks in natural language. You produce queries.

                Else: if user wants to stop the playback - use the stop playback tool.
            """,
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    llm = openai.LLM(model="gpt-4.1-mini")
    # llm = openai.LLM.with_ollama(model="qwen3:4b", base_url="http://localhost:11434/v1")

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=llm,
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(),
    )

    await session.generate_reply(
        instructions="""
        Greet the user and offer your assistance.
        You don't tell about your thinking process.
        You are only the conversational assistant.
        You can use tools that are available to you.
        """
    )


if __name__ == "__main__":

    # Run the worker
    print("Running worker...")
    print("LIVEKIT_API_KEY: ", os.getenv("LIVEKIT_API_KEY"))
    print("LIVEKIT_ENDPOINT: ", os.getenv("LIVEKIT_URL"))
    print("LIVEKIT_SECRET: ", os.getenv("LIVEKIT_API_SECRET"))

    print("ELEVENLABS_API_KEY: ", os.getenv("ELEVEN_API_KEY"))
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

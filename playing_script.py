# in play.py (pure-Spotipy)
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = "https://1f27-212-75-103-72.ngrok-free.app/callback"  # ← your ngrok HTTPS URL     # ← no port here! ngrok maps 443→5000

SCOPE = "user-read-playback-state user-modify-playback-state"

sp = Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
)

devices = sp.devices()

print("Devices:", [d["name"] for d in devices["devices"]])

device_id = devices["devices"][0]["id"]


def search_for_track_id(query, market="US", limit=10):
    """
    Performs a full-text search for tracks and returns their IDs.

    Args:
        query (str): The search query string (e.g., "Bohemian Rhapsody Queen",
                     "track:Doxy artist:Miles Davis").
        market (str): An ISO 3166-1 alpha-2 country code.
        limit (int): The maximum number of results to return.

    Returns:
        list: A list of dictionaries, each containing 'name', 'artist', and 'id'
              for the found tracks.
    """
    results = sp.search(q=query, type="track", market=market, limit=limit)
    tracks_info = []
    for item in results["tracks"]["items"]:
        track_name = item["name"]
        artist_name = item["artists"][0]["name"]  # Get the first artist's name
        track_id = item["id"]
        tracks_info.append({"name": track_name, "artist": artist_name, "id": track_id})
    return tracks_info


def start_playback(song_id: str):
    sp.start_playback(
        device_id=device_id,  # or set to one of the IDs you saw above
        uris=[f"spotify:track:{song_id}"],
    )


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

    track_info = search_for_track_id(spotify_query_text, limit=1)
    start_playback(track_info[0]["id"])


if __name__ == "__main__":

    from openai import OpenAI

    client = OpenAI()

    SYSTEM_PROMPT = """
        You are a helpful assistant.
        Your only task is to produce queries to search for the spotify tracks.

        Example queries:
        - "genre:jazz year:1960-1970"
        - "Shape of You Ed Sheeran"
        - "track:Crazy Little Thing Called Love artist:Queen"

        You need to produce the queries to spotify based of what you receive from user.
        User speaks in natural language. You produce queries
    """
    USER_PROMPT = """
        Current question: {}
        Query:
    """

    user_query = input("What do you want to listen to: ")

    input_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT.format(user_query)},
    ]
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=input_messages,
    )

    spotify_query_text = response.output[0].content[0].text
    track_info = search_for_track_id(spotify_query_text, limit=1)

    start_playback(track_info[0]["id"])

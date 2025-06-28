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


class SpotifyPlayer:
    def __init__(self):
        self.sp = Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
            )
        )
        devices = self.sp.devices()
        print("Devices:", [d["name"] for d in devices["devices"]])
        self.device_id = devices["devices"][0]["id"]

    def search_for_track_id(self, query, market="US", limit=10):
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
        results = self.sp.search(q=query, type="track", market=market, limit=limit)
        tracks_info = []
        for item in results["tracks"]["items"]:
            track_name = item["name"]
            artist_name = item["artists"][0]["name"]  # Get the first artist's name
            track_id = item["id"]
            tracks_info.append(
                {"name": track_name, "artist": artist_name, "id": track_id}
            )
        return tracks_info

    def start_playback(self, song_id: str):
        self.sp.start_playback(
            device_id=self.device_id,  # or set to one of the IDs you saw above
            uris=[f"spotify:track:{song_id}"],
        )

    def stop_current_playback(self):
        self.sp.pause_playback()


player_client = SpotifyPlayer()

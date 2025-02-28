# Import necessary libraries
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from pymongo import MongoClient
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, MONGO_URI

# Set up Spotify access
scope = "user-library-read playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

# Define functions to fetch data
def get_tracks_from_playlist(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def get_audio_features(track_ids):
    features = sp.audio_features(track_ids)
    return features

def get_artist_info(artist_id):
    artist = sp.artist(artist_id)
    return artist

def get_album_info(album_id):
    album = sp.album(album_id)
    return album

# Fetch and combine data
playlist_id = 'your_playlist_id'
tracks = get_tracks_from_playlist(playlist_id)
track_ids = [track['track']['id'] for track in tracks]
audio_features = get_audio_features(track_ids)

track_data = []
for track in tracks:
    track_info = {
        'track_id': track['track']['id'],
        'track_name': track['track']['name'],
        'artist_id': track['track']['artists'][0]['id'],
        'artist_name': track['track']['artists'][0]['name'],
        'album_id': track['track']['album']['id'],
        'album_name': track['track']['album']['name'],
        'release_date': track['track']['album']['release_date']
    }
    track_data.append(track_info)

track_df = pd.DataFrame(track_data)
audio_features_df = pd.DataFrame(audio_features)
combined_df = track_df.merge(audio_features_df, left_on='track_id', right_on='id')

# Save data to MongoDB
client = MongoClient(MONGO_URI)
db = client['spotify_data']
collection = db['tracks']

# Convert DataFrame to dictionary and insert into MongoDB
data_dict = combined_df.to_dict("records")
collection.insert_many(data_dict)

print("Data inserted successfully!")
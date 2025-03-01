import requests
import logging
import pandas as pd
from pymongo import MongoClient
from config import CLIENT_ID, CLIENT_SECRET, MONGO_URI
from fetch_spotify_data import *
from data_ids import playlist_ids, artist_ids, album_ids, user_ids

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to get access token
def get_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()
    return response_data['access_token']

# Set up Spotify access
access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
sp = spotipy.Spotify(auth=access_token)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['spotify_data']

# Fetch and save track data
for playlist_id in playlist_ids:
    tracks = get_tracks_from_playlist(sp, playlist_id)
    track_ids = [track['track']['id'] for track in tracks]
    audio_features = get_audio_features(sp, track_ids)
    
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
    
    # Save to CSV
    combined_df.to_csv('tracks.csv', index=False)
    
    # Save to MongoDB
    collection = db['tracks']
    data_dict = combined_df.to_dict("records")
    collection.insert_many(data_dict)

# Fetch and save artist data
for artist_id in artist_ids:
    artist_info = get_artist_info(sp, artist_id)
    artist_df = pd.DataFrame([artist_info])
    
    # Save to CSV
    artist_df.to_csv('artists.csv', index=False)
    
    # Save to MongoDB
    collection = db['artists']
    data_dict = artist_df.to_dict("records")
    collection.insert_many(data_dict)

# Fetch and save album data
for album_id in album_ids:
    album_info = get_album_info(sp, album_id)
    album_df = pd.DataFrame([album_info])
    
    # Save to CSV
    album_df.to_csv('albums.csv', index=False)
    
    # Save to MongoDB
    collection = db['albums']
    data_dict = album_df.to_dict("records")
    collection.insert_many(data_dict)

# Fetch and save top tracks data
for artist_id in artist_ids:
    top_tracks = get_top_tracks(sp, artist_id)
    top_tracks_df = pd.DataFrame(top_tracks)
    
    # Save to CSV
    top_tracks_df.to_csv('top_tracks.csv', index=False)
    
    # Save to MongoDB
    collection = db['top_tracks']
    data_dict = top_tracks_df.to_dict("records")
    collection.insert_many(data_dict)

# Fetch and save related artists data
for artist_id in artist_ids:
    related_artists = get_related_artists(sp, artist_id)
    related_artists_df = pd.DataFrame(related_artists)
    
    # Save to CSV
    related_artists_df.to_csv('related_artists.csv', index=False)
    
    # Save to MongoDB
    collection = db['related_artists']
    data_dict = related_artists_df.to_dict("records")
    collection.insert_many(data_dict)

# Fetch and save genres data
genres = get_genres(sp)
genres_df = pd.DataFrame(genres, columns=['genre'])
    
# Save to CSV
genres_df.to_csv('genres.csv', index=False)
    
# Save to MongoDB
collection = db['genres']
data_dict = genres_df.to_dict("records")
collection.insert_many(data_dict)

# Fetch and save markets data
markets = get_markets(sp)
markets_df = pd.DataFrame(markets, columns=['market'])
    
# Save to CSV
markets_df.to_csv('markets.csv', index=False)
    
# Save to MongoDB
collection = db['markets']
data_dict = markets_df.to_dict("records")
collection.insert_many(data_dict)

# Fetch and save playlists data
for user_id in user_ids:
    playlists = get_playlists(sp, user_id)
    playlists_df = pd.DataFrame(playlists)
    
    # Save to CSV
    playlists_df.to_csv('playlists.csv', index=False)
    
    # Save to MongoDB
    collection = db['playlists']
    data_dict = playlists_df.to_dict("records")
    collection.insert_many(data_dict)

print("Data inserted successfully!")

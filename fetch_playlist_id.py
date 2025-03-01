import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests
from config import CLIENT_ID, CLIENT_SECRET

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

# Function to fetch playlist IDs based on a keyword
def get_playlist_ids(keyword, limit=50):
    results = sp.search(q=keyword, type='playlist', limit=limit)
    if results and 'playlists' in results and 'items' in results['playlists']:
        playlist_ids = [{'playlist_id': playlist['id'], 'playlist_name': playlist['name']} for playlist in results['playlists']['items']]
        return playlist_ids
    else:
        return []

# Keywords to search for
keywords = ['rock', 'pop', 'jazz', 'classical', 'hip hop']

# Fetch playlist IDs for each keyword and save to a list
all_playlists = []
for keyword in keywords:
    playlists = get_playlist_ids(keyword)
    all_playlists.extend(playlists)
    print(f"Playlists for keyword '{keyword}':")
    for playlist in playlists:
        print(f"ID: {playlist['playlist_id']}, Name: {playlist['playlist_name']}")

# Save the results to a CSV file
df = pd.DataFrame(all_playlists)
df.to_csv('playlists.csv', index=False)

print("Playlist IDs have been saved to 'playlists.csv'.")
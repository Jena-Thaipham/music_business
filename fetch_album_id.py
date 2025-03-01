import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from config import CLIENT_ID, CLIENT_SECRET

# Set up Spotify access
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Function to fetch album IDs based on a keyword
def get_album_ids(keyword, limit=50):
    results = sp.search(q=keyword, type='album', limit=limit)
    album_ids = [{'album_id': album['id'], 'album_name': album['name']} for album in results['albums']['items']]
    return album_ids

# Keywords to search for
keywords = ['rock', 'pop', 'jazz', 'classical', 'hip hop']

# Fetch album IDs for each keyword and save to a list
all_albums = []
for keyword in keywords:
    albums = get_album_ids(keyword)
    all_albums.extend(albums)

# Save the results to a CSV file
df_albums = pd.DataFrame(all_albums)
df_albums.to_csv('albums.csv', index=False)

print("Album IDs have been saved to 'albums.csv'.")
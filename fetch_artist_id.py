import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from config import CLIENT_ID, CLIENT_SECRET

# Set up Spotify access
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Function to fetch artist IDs based on a keyword
def get_artist_ids(keyword, limit=50):
    results = sp.search(q=keyword, type='artist', limit=limit)
    artist_ids = [{'artist_id': artist['id'], 'artist_name': artist['name']} for artist in results['artists']['items']]
    return artist_ids

# Keywords to search for
keywords = ['rock', 'pop', 'jazz', 'classical', 'hip hop']

# Fetch artist IDs for each keyword and save to a list
all_artists = []
for keyword in keywords:
    artists = get_artist_ids(keyword)
    all_artists.extend(artists)

# Save the results to a CSV file
df_artists = pd.DataFrame(all_artists)
df_artists.to_csv('artists.csv', index=False)

print("Artist IDs have been saved to 'artists.csv'.")
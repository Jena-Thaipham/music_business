import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from config import CLIENT_ID, CLIENT_SECRET

# Set up Spotify access
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Function to fetch user IDs based on a keyword
def get_user_ids(keyword, limit=50):
    results = sp.search(q=keyword, type='user', limit=limit)
    user_ids = [{'user_id': user['id'], 'user_name': user['display_name']} for user in results['users']['items']]
    return user_ids

# Keywords to search for
keywords = ['rock', 'pop', 'jazz', 'classical', 'hip hop']

# Fetch user IDs for each keyword and save to a list
all_users = []
for keyword in keywords:
    users = get_user_ids(keyword)
    all_users.extend(users)

# Save the results to a CSV file
df_users = pd.DataFrame(all_users)
df_users.to_csv('users.csv', index=False)

print("User IDs have been saved to 'users.csv'.")
import requests
import base64
import random
import logging
from dotenv import load_dotenv
import os

def get_access_token():
    load_dotenv()
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}",
            }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        logging.error(f"Error: {response.status_code} - {response.text}")

def get_random_album_ids(access_token, count=40):
    url = 'https://api.spotify.com/v1/browse/new-releases'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        albums = response.json()['albums']['items']
        sample_size = min(count, len(albums))
        album_ids = [album['id'] for album in random.sample(albums, sample_size)]
        return album_ids
    else:
        logging.error(f"Error fetching albums: {response.status_code} - {response.text}")
        return []

def get_random_artist_ids(access_token, count=40):
    url = 'https://api.spotify.com/v1/search?q=%25a%25&type=artist&limit=50'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        artists = response.json()['artists']['items']
        sample_size = min(count, len(artists))
        artist_ids = [artist['id'] for artist in random.sample(artists, sample_size)]
        return artist_ids
    else:
        logging.error(f"Error fetching artists: {response.status_code} - {response.text}")
        return []

def get_random_track_ids(access_token, count=40):
    url = 'https://api.spotify.com/v1/search?q=%25a%25&type=track&limit=50'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tracks = response.json()['tracks']['items']
        sample_size = min(count, len(tracks))
        track_ids = [track['id'] for track in random.sample(tracks, sample_size)]
        return track_ids
    else:
        logging.error(f"Error fetching tracks: {response.status_code} - {response.text}")
        return []

def get_random_playlist_ids(access_token, count=40):
    url = 'https://api.spotify.com/v1/browse/featured-playlists'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        playlists = response.json()['playlists']['items']
        sample_size = min(count, len(playlists))
        playlist_ids = [playlist['id'] for playlist in random.sample(playlists, sample_size)]
        return playlist_ids
    else:
        logging.error(f"Error fetching playlists: {response.status_code} - {response.text}")
        return []

def save_ids_to_file(ids, filename):
    with open(filename, 'w') as file:
        for id in ids:
            file.write(f"{id}\n")

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    access_token = get_access_token()
    
    album_ids = get_random_album_ids(access_token)
    artist_ids = get_random_artist_ids(access_token)
    track_ids = get_random_track_ids(access_token)
    playlist_ids = get_random_playlist_ids(access_token)
    
    if album_ids:
        save_ids_to_file(album_ids, 'album_ids.txt')
    if artist_ids:
        save_ids_to_file(artist_ids, 'artist_ids.txt')
    if track_ids:
        save_ids_to_file(track_ids, 'track_ids.txt')
    if playlist_ids:
        save_ids_to_file(playlist_ids, 'playlist_ids.txt')
    
    logging.info("Random IDs saved to files successfully!")

if __name__ == "__main__":
    main()
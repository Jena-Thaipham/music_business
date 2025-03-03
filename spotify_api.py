import requests
import base64
import json 
import pandas as pd
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

def get_album_info(album_id, access_token):
    url = f'https://api.spotify.com/v1/albums/{album_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        album_data = response.json()
        for key, value in album_data.items():
            if isinstance(value, (list, dict)): 
                album_data[key] = json.dumps(value)  
        
        return album_data
    else:
         logging.error(f"Error fetching album {album_id}: {response.status_code} - {response.text}")

def get_artist_info(artist_id, access_token):
    url = f'https://api.spotify.com/v1/artists/{artist_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        artist_data = response.json()
        for key, value in artist_data.items():
            if isinstance(value, (list, dict)):  
                artist_data[key] = json.dumps(value)  
        
        return artist_data
    else:
         logging.error(f"Error fetching artist {artist_id}: {response.status_code} - {response.text}")

def extract_album_data_to_df(album_ids, access_token):
   albums_data = []
   for album_id in album_ids:
        album_info = get_album_info(album_id, access_token)
        if album_info:
            albums_data.append(album_info)
   return pd.DataFrame(albums_data)

def extract_artist_data_to_df(artist_ids, access_token):
    artists_data = []
    for artist_id in artist_ids:
        artist_info = get_artist_info(artist_id, access_token)
        if artist_info:
            artists_data.append(artist_info)
    return pd.DataFrame(artists_data)

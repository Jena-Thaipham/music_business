import requests
import base64
import json 
from config import CLIENT_ID, CLIENT_SECRET

def get_access_token():
    """
    Fetches an access token using the Client Credentials Flow.
    """
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}",
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_album_info(album_id, access_token):
    """
    Fetches all album information using the Spotify API.
    """
    url = f'https://api.spotify.com/v1/albums/{album_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        album_data = response.json()
        
        # Convert all list fields to JSON strings
        for key, value in album_data.items():
            if isinstance(value, (list, dict)): 
                album_data[key] = json.dumps(value)  
        
        return album_data
    else:
        print(f"Error fetching album {album_id}: {response.status_code} - {response.text}")
        return None

def get_artist_info(artist_id, access_token):
    """
    Fetches all artist information using the Spotify API.
    """
    url = f'https://api.spotify.com/v1/artists/{artist_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        artist_data = response.json()
        
        # Convert all list fields to JSON strings
        for key, value in artist_data.items():
            if isinstance(value, (list, dict)):  
                artist_data[key] = json.dumps(value)  
        
        return artist_data
    else:
        print(f"Error fetching artist {artist_id}: {response.status_code} - {response.text}")
        return None
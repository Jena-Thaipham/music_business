import requests
import base64
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
        return response.json()  # Return the entire album data
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
        return response.json()  # Return the entire artist data
    else:
        print(f"Error fetching artist {artist_id}: {response.status_code} - {response.text}")
        return None
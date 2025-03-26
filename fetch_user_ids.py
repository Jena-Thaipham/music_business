import requests
import random
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
import os
import base64

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        return None

def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504, 429]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def safe_request(session, url, headers):
    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))
            logging.warning(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after + random.random())
            return safe_request(session, url, headers)
        response.raise_for_status()
        return response
    except (requests.exceptions.RequestException, ConnectionError) as e:
        logging.error(f"Request failed: {str(e)}")
        return None

def get_random_user_ids(access_token, count=50):
    session = create_session()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    user_ids = set()
    
    albums_url = "https://api.spotify.com/v1/me/albums?limit=20"
    while albums_url and len(user_ids) < count:
        response = safe_request(session, albums_url, headers)
        if not response:
            break
            
        data = response.json()
        for item in data.get('items', []):
            for artist in item.get('album', {}).get('artists', []):
                if artist.get('id'):
                    user_ids.add(artist['id'])
        
        albums_url = data.get('next')
        time.sleep(1 + random.random())
    
    playlists_url = "https://api.spotify.com/v1/me/playlists?limit=20"
    while playlists_url and len(user_ids) < count:
        response = safe_request(session, playlists_url, headers)
        if not response:
            break
            
        data = response.json()
        for playlist in data.get('items', []):
            owner_id = playlist.get('owner', {}).get('id')
            if owner_id:
                user_ids.add(owner_id)
        
        playlists_url = data.get('next')
        time.sleep(1 + random.random())
    
    session.close()
    return random.sample(list(user_ids), min(count, len(user_ids))) if user_ids else []

if __name__ == "__main__":
    access_token = get_access_token()
    user_ids = get_random_user_ids(access_token)
    logging.info(f"Fetched {len(user_ids)} user IDs")
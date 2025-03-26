import requests
import base64
import random
import logging
from dotenv import load_dotenv
import os
import time

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

def fetch_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  
                retry_after = int(response.headers.get('Retry-After', 5))
                logging.warning(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            else:
                logging.error(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)  
    return None

def get_random_ids(access_token, item_type, count=40):
    base_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    search_terms = ['%25a%25', '%25e%25', '%25i%25', '%25o%25', '%25u%25',
                   '%25the%25', '%25and%25', '%25best%25', '%25top%25', '%25mix%25']
    random.shuffle(search_terms)
    
    ids = set()
    for term in search_terms:
        if len(ids) >= count:
            break
            
        url = f"{base_url}?q={term}&type={item_type}&limit=50"
        response = fetch_with_retry(url, headers)
        
        if response and response.status_code == 200:
            items = response.json().get(f"{item_type}s", {}).get("items", [])
            for item in items:
                if item and 'id' in item:
                    ids.add(item['id'])
        
        time.sleep(0.5)
    
    return random.sample(list(ids), min(count, len(ids))) if ids else []
    
def get_random_user_ids(access_token, count=40):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    popular_playlists = [
        '37i9dQZEVXbMDoHDwVN2tF',  
        '37i9dQZEVXbLRQDuF5jeBp',  
        '37i9dQZEVXbLiRSasKsNU9'   
    ]
    
    user_ids = set()
    
    for playlist_id in popular_playlists:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        response = fetch_with_retry(url, headers)
        
        if response and response.status_code == 200:
            playlist = response.json()
            if 'owner' in playlist and 'id' in playlist['owner']:
                user_ids.add(playlist['owner']['id'])
        
        tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50"
        tracks_response = fetch_with_retry(tracks_url, headers)
        
        if tracks_response and tracks_response.status_code == 200:
            tracks = tracks_response.json().get('items', [])
            for track in tracks:
                if track and 'added_by' in track and 'id' in track['added_by']:
                    user_ids.add(track['added_by']['id'])
        
        time.sleep(0.5)
    
    return random.sample(list(user_ids), min(count, len(user_ids))) if user_ids else []

def save_ids_to_file(ids, filename):
    existing_ids = set()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_ids = set(line.strip() for line in file.readlines())
    
    new_ids = set(ids) - existing_ids
    
    with open(filename, 'a') as file:
        for id in new_ids:
            file.write(f"{id}\n")
    
    return len(new_ids)  

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    access_token = get_access_token()
    
    if not access_token:
        logging.error("Failed to get access token. Exiting.")
        return
    
    album_count = save_ids_to_file(get_random_ids(access_token, 'album', 50), 'album_ids.txt')
    artist_count = save_ids_to_file(get_random_ids(access_token, 'artist', 50), 'artist_ids.txt')
    track_count = save_ids_to_file(get_random_ids(access_token, 'track', 50), 'track_ids.txt')
    playlist_count = save_ids_to_file(get_random_ids(access_token, 'playlist', 50), 'playlist_ids.txt')
    user_count = save_ids_to_file(get_random_user_ids(access_token, 50), 'user_ids.txt')
    
    logging.info(f"Added {album_count} new albums, {artist_count} new artists, "
                f"{track_count} new tracks, {playlist_count} new playlists, "
                f"and {user_count} new users to files.")

if __name__ == "__main__":
    main()
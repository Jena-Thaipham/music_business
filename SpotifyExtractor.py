import random
import time
import requests
import base64
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set
from dotenv import load_dotenv

class SpotifyExtractor:
    def __init__(self):
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self) -> Optional[str]:
        if self.access_token and datetime.now() < self.token_expiry:
            return self.access_token
            
        auth_string = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}
        
        try:
            response = requests.post('https://accounts.spotify.com/api/token', 
                                  headers=headers, 
                                  data=data,
                                  timeout=10)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'] - 60)
            return self.access_token
        except Exception as e:
            logging.error(f"Error getting access token: {str(e)}")
            return None

    def make_request(self, endpoint: str) -> Optional[Dict]:
        headers = {'Authorization': f'Bearer {self.get_access_token()}'}
        
        try:
            response = requests.get(f'https://api.spotify.com/v1/{endpoint}', 
                                  headers=headers, 
                                  timeout=15)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                self.access_token = None
                return self.make_request(endpoint)
            else:
                logging.error(f"API error {response.status_code} for {endpoint}")
                return None
        except Exception as e:
            logging.error(f"Request failed: {str(e)}")
            return None

    def get_playlist_info(self, playlist_id: str) -> Optional[Dict]:
        data = self.make_request(f'playlists/{playlist_id}')
        if not data:
            return None
            
        try:
            return {
                'playlist_id': data['id'],
                'playlist_name': data['name'],
                'owner_id': data['owner']['id'],
                'total_tracks': data['tracks']['total'],
                'playlist_followers': data['followers']['total'],
                'public': bool(data['public']),
                'playlist_uri': data['uri'],
            }
        except KeyError as e:
            logging.error(f"Missing field in playlist data: {str(e)}")
            return None

    def get_album_info(self, album_id: str) -> Optional[Dict]:
        data = self.make_request(f'albums/{album_id}')
        if not data:
            return None
            
        try:
            return {
                'album_id': data['id'],
                'album_name': data['name'],
                'album_type': data['album_type'],
                'artist_id': data['artists'][0]['id'],
                'artist_name': data['artists'][0]['name'],
                'release_date': data['release_date'],
                'total_tracks': data['total_tracks'],
                'album_uri': data['uri']
            }
        except (KeyError, IndexError) as e:
            logging.error(f"Missing field in album data: {str(e)}")
            return None

    def get_artist_info(self, artist_id: str) -> Optional[Dict]:
        data = self.make_request(f'artists/{artist_id}')
        if not data:
            return None
            
        try:
            return {
                'artist_id': data['id'],
                'artist_name': data['name'],
                'followers': data['followers']['total'],
                'artist_uri': data['uri']
            }
        except KeyError as e:
            logging.error(f"Missing field in artist data: {str(e)}")
            return None

    def get_track_info(self, track_id: str) -> Optional[Dict]:
        data = self.make_request(f'tracks/{track_id}')
        if not data:
            return None
            
        try:
            return {
                'track_id': data['id'],
                'track_name': data['name'],
                'artist_id': data['artists'][0]['id'],
                'album_id': data['album']['id'],
                'duration_ms': data['duration_ms'],
                'track_uri': data['uri']
            }
        except (KeyError, IndexError) as e:
            logging.error(f"Missing field in track data: {str(e)}")
            return None

    def get_playlist_tracks(self, playlist_id: str) -> Optional[List[Dict]]:
        data = self.make_request(f'playlists/{playlist_id}/tracks?limit=100')
        if not data:
            return None
            
        tracks = []
        while data:
            try:
                tracks.extend([{
                    'playlist_id': playlist_id,
                    'track_id': item['track']['id'],
                    'added_at': item['added_at']
                } for item in data['items'] if item.get('track')])
            except KeyError:
                continue
                
            if data['next']:
                data = self.make_request(data['next'].replace('https://api.spotify.com/v1/', ''))
            else:
                data = None
                
        return tracks if tracks else None

    def check_playlist_availability(self, playlist_id: str) -> bool:
        try:
            response = requests.get(
                f"https://api.spotify.com/v1/playlists/{playlist_id}",
                headers={'Authorization': f'Bearer {self.get_access_token()}'},
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        headers = {'Authorization': f'Bearer {self.get_access_token()}'}
        
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

    def _read_ids_from_file(self, filename: str) -> List[str]:
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.warning(f"ID file not found: {filename}")
            return []

    

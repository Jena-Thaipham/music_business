import requests
import base64
import json
import pandas as pd
import logging
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SpotifyAPI:
    def __init__(self):
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.access_token = None
        self.token_expiry = None
        
        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            raise ValueError("Spotify API credentials not found in .env file")

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

class DatabaseManager:
    def __init__(self, db_path: str = "spotify.db", schema_dir: str = "spotify_db/schema"):
        self.db_path = db_path
        self.schema_dir = schema_dir
        self.connection = None
        self._initialize_database()
        
    def _load_schema_file(self, filename: str) -> str:
        schema_path = Path(self.schema_dir) / filename
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logging.error(f"Schema file not found: {schema_path}")
            raise
        except Exception as e:
            logging.error(f"Error reading schema file: {str(e)}")
            raise
        
    def _initialize_database(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            schema_files = [
                'create_artist_schema.sql',
                'create_user_schema.sql',
                'create_album_schema.sql',
                'create_track_schema.sql',
                'create_playlist_schema.sql',
                'create_playlist_track_schema.sql'
            ]
            
            for schema_file in schema_files:
                try:
                    sql = self._load_schema_file(schema_file)
                    cursor.executescript(sql)
                except Exception as e:
                    logging.error(f"Error executing schema {schema_file}: {str(e)}")
                    raise
                    
            self.connection.commit()
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {str(e)}")
            if self.connection:
                self.connection.close()
            raise
            
    def save_data(self, dataframes: Dict[str, pd.DataFrame]) -> bool:
        if not self.connection:
            logging.error("Database connection not established")
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            tables = [
                'artists',
                'users',
                'albums',
                'tracks',
                'playlists', 
                'playlist_tracks'
            ]
            
            for table in tables:
                if table in dataframes and not dataframes[table].empty:
                    df = dataframes[table].where(pd.notnull(dataframes[table]), None)
                    
                    columns = ', '.join(df.columns)
                    placeholders = ', '.join(['?'] * len(df.columns))
                    
                    sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
                    
                    try:
                        data_tuples = [tuple(x) for x in df.to_numpy()]
                        cursor.executemany(sql, data_tuples)
                        logging.info(f"Inserted {len(data_tuples)} rows into {table}")
                    except sqlite3.Error as e:
                        logging.error(f"Error inserting into {table}: {str(e)}")
                        continue
            
            self.connection.commit()  
            logging.info("All changes committed to database")
            return True
        except Exception as e:
            self.connection.rollback()
            logging.error(f"Transaction rolled back: {str(e)}")
            return False
            
    def close(self):
        if self.connection:
            self.connection.close()

def read_ids_from_file(file_path: str) -> List[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}")
        return []
    except Exception as e:
        logging.error(f"Error reading file: {str(e)}")
        return []

def main():
    spotify = SpotifyAPI()
    db_manager = DatabaseManager()
    
    try:
        album_ids = read_ids_from_file('album_ids.txt')
        artist_ids = read_ids_from_file('artist_ids.txt')
        track_ids = read_ids_from_file('track_ids.txt')
        playlist_ids = read_ids_from_file('playlist_ids.txt')
        
        data_to_save = {}
        
        # Fetch all data independently
        if artist_ids:
            logging.info("Fetching artist data...")
            artists_data = [spotify.get_artist_info(aid) for aid in artist_ids]
            data_to_save['artists'] = pd.DataFrame(filter(None, artists_data))
        
        if album_ids:
            logging.info("Fetching album data...")
            albums_data = [spotify.get_album_info(aid) for aid in album_ids]
            data_to_save['albums'] = pd.DataFrame(filter(None, albums_data))
        
        if track_ids:
            logging.info("Fetching track data...")
            tracks_data = [spotify.get_track_info(tid) for tid in track_ids]
            data_to_save['tracks'] = pd.DataFrame(filter(None, tracks_data))
        
        if playlist_ids:
            logging.info("Fetching playlist data...")
            playlists = []
            users = []
            valid_playlist_ids = []
            
            for pid in playlist_ids:
                if spotify.check_playlist_availability(pid):
                    playlist = spotify.get_playlist_info(pid)
                    if playlist:
                        playlists.append(playlist)
                        users.append({
                            'user_id': playlist['owner_id'],
                            'user_uri': f"spotify:user:{playlist['owner_id']}"
                        })
                        valid_playlist_ids.append(pid)
            
            if playlists:
                data_to_save['playlists'] = pd.DataFrame(playlists)
                data_to_save['users'] = pd.DataFrame(users)
                
                logging.info("Fetching playlist tracks...")
                playlist_tracks = []
                for pid in valid_playlist_ids:
                    tracks = spotify.get_playlist_tracks(pid)
                    if tracks:
                        playlist_tracks.extend(tracks)
                
                if playlist_tracks:
                    data_to_save['playlist_tracks'] = pd.DataFrame(playlist_tracks)

        if data_to_save:
            logging.info("Saving data to database...")
            if db_manager.save_data(data_to_save):
                logging.info("Data saved successfully")
            else:
                logging.warning("Some data may not have been saved")
        else:
            logging.warning("No data to save")
            
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()
import sqlite3
import logging
from typing import Optional, List
import pandas as pd
from spotify_api import (
    get_access_token,
    extract_album_data_to_df,
    extract_artist_data_to_df,
    extract_track_data_to_df,
    extract_playlist_data_to_df,
    extract_playlist_tracks_to_df
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def read_ids_from_file(file_path: str) -> List[str]:
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise

def create_database(db_path: str = "spotify_db/spotify.db") -> Optional[sqlite3.Connection]:
    
    SCHEMA_FILES = [
        "create_user_schema.sql",
        "create_artist_schema.sql",
        "create_album_schema.sql",
        "create_track_schema.sql",
        "create_playlist_schema.sql",
        "create_playlist_track_schema.sql",
        "create_listening_history_schema.sql"
    ]

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        connection.execute("BEGIN TRANSACTION")

        for schema_file in SCHEMA_FILES:
            try:
                with open(f"spotify_db/schema/{schema_file}", "r") as f:
                    cursor.executescript(f.read())
                logging.info(f"Created table(s) from {schema_file}")
            except FileNotFoundError:
                logging.error(f"Schema file missing: {schema_file}")
                raise
            except sqlite3.Error as e:
                logging.error(f"SQL error in {schema_file}: {e}")
                raise

        connection.commit()
        return connection

    except Exception as e:
        logging.critical(f"Database creation failed: {e}")
        if 'connection' in locals():
            connection.rollback()
        return None

def main():
    access_token = get_access_token()
    if not access_token:
        logging.error("Failed to get Spotify access token!")
        return

    try:
        album_ids = read_ids_from_file("album_ids.txt")
        artist_ids = read_ids_from_file("artist_ids.txt")
        track_ids = read_ids_from_file("track_ids.txt")
        playlist_ids = read_ids_from_file("playlist_ids.txt")
    except FileNotFoundError as e:
        logging.error(f"ID file missing: {e}")
        return

    artists_df = extract_artist_data_to_df(artist_ids, access_token)
    albums_df = extract_album_data_to_df(album_ids, access_token)
    tracks_df = extract_track_data_to_df(track_ids, access_token)
    playlists_df = extract_playlist_data_to_df(playlist_ids, access_token)
    playlist_tracks_df = extract_playlist_tracks_to_df(playlist_ids, access_token)

    conn = create_database()
    if not conn:
        return

    try:
        artists_df.to_sql('artists', conn, if_exists='append', index=False)
        albums_df.to_sql('albums', conn, if_exists='append', index=False)
        tracks_df.to_sql('tracks', conn, if_exists='append', index=False)
        playlists_df.to_sql('playlists', conn, if_exists='append', index=False)
        playlist_tracks_df.to_sql('playlist_tracks', conn, if_exists='append', index=False)
        logging.info("Data inserted successfully!")
    except sqlite3.Error as e:
        logging.error(f"Data insertion failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
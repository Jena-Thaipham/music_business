import sqlite3
import pandas as pd
import os
import json
import logging
from spotify_api import get_access_token, get_album_info, get_artist_info, get_track_info, get_playlist_info, get_playlist_tracks, extract_album_data_to_df, extract_artist_data_to_df, extract_track_data_to_df, extract_playlist_data_to_df, extract_playlist_tracks_to_df

def read_ids_from_txt(file_path):
    ids = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:  
                ids.append(line)
    return ids

def create_database():
    connection = sqlite3.connect("spotify_db/spotify.db")
    cursor = connection.cursor()

    with open('spotify_db/schema/create_artist_schema.sql', 'r') as file:
        create_artist_table_query = file.read()
    cursor.execute(create_artist_table_query)
    
    with open('spotify_db/schema/create_album_schema.sql', 'r') as file:
        create_album_table_query = file.read()
    cursor.execute(create_album_table_query)

    with open('spotify_db/schema/create_user_schema.sql', 'r') as file:
        create_user_table_query = file.read()  
    cursor.execute(create_user_table_query)

    with open('spotify_db/schema/create_track_schema.sql', 'r') as file:
        create_track_table_query = file.read()
    cursor.execute(create_track_table_query)

    with open('spotify_db/schema/create_playlist_schema.sql', 'r') as file:
        create_playlist_table_query = file.read()
    cursor.execute(create_playlist_table_query)

    with open('spotify_db/schema/create_playlist_track_schema.sql', 'r') as file:
        create_playlist_tracks_table_query = file.read()
    cursor.execute(create_playlist_tracks_table_query)

    with open('spotify_db/schema/create_listening_history_schema.sql', 'r') as file:
        create_listening_history_table_query = file.read()
    cursor.execute(create_listening_history_table_query)


    connection.commit()
    return connection

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    access_token = get_access_token()
        
    album_ids = read_ids_from_txt('album_ids.txt')
    artist_ids = read_ids_from_txt('artist_ids.txt')
    track_ids = read_ids_from_txt('track_ids.txt')
    playlist_ids = read_ids_from_txt('playlist_ids.txt')

    albums_df = extract_album_data_to_df(album_ids, access_token)
    artists_df = extract_artist_data_to_df(artist_ids, access_token)
    tracks_df = extract_track_data_to_df(track_ids, access_token)
    playlists_df = extract_playlist_data_to_df(playlist_ids, access_token)
    playlist_tracks_df = extract_playlist_tracks_to_df(playlist_ids, access_token)

    print("Columns in playlists_df:", playlists_df.columns.tolist())
    print("Data types:\n", playlists_df.dtypes)
    print("First few rows:\n", playlists_df.head())
    
    connection = create_database()
    albums_df.to_sql('albums', connection, if_exists='replace', index=False)
    artists_df.to_sql('artists', connection, if_exists='replace', index=False)
    tracks_df.to_sql('tracks', connection, if_exists='replace', index=False)
    playlists_df.to_sql('playlists', connection, if_exists='replace', index=False)
    playlist_tracks_df.to_sql('playlist_tracks', connection, if_exists='replace', index=False)

    connection.close()
    logging.info("Data saved to database successfully!")

if __name__ == "__main__":
    main()
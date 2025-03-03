# export_data_to_database.py
import sqlite3
import pandas as pd
import os
import json
from spotify_api import get_access_token, get_album_info, get_artist_info
from file_utils import read_ids_from_txt, save_to_csv

def create_database():
    """
    Create the database and tables using the schema files.
    """
    # Create the spotify_db directory if it doesn't exist
    os.makedirs("spotify_db", exist_ok=True)

    # Connect to the database (create a new one if it doesn't exist)
    connection = sqlite3.connect("spotify_db/spotify.db")
    cursor = connection.cursor()

    # Create the albums table
    with open('spotify_db/schema/create_album_schema.sql', 'r') as file:
        create_album_table_query = file.read()
    cursor.execute(create_album_table_query)

    # Create the artists table
    with open('spotify_db/schema/create_artist_schema.sql', 'r') as file:
        create_artist_table_query = file.read()
    cursor.execute(create_artist_table_query)

    connection.commit()
    return connection

def save_albums_to_database(albums_data, connection):
    """
    Save album data to the database.
    """
    albums_df = pd.DataFrame(albums_data)
    albums_df.to_sql('albums', connection, if_exists='replace', index=False)

def save_artists_to_database(artists_data, connection):
    """
    Save artist data to the database.
    """
    artists_df = pd.DataFrame(artists_data)
    artists_df.to_sql('artists', connection, if_exists='replace', index=False)

def main():
    # Fetch access token
    access_token = get_access_token()
    if not access_token:
        print("Failed to get access token.")
        return

    # Read album and artist IDs from text files
    album_ids = read_ids_from_txt('album_ids.txt')
    artist_ids = read_ids_from_txt('artist_ids.txt')

    # Fetch album and artist data
    albums_data = []
    artists_data = []

    for album_id in album_ids:
        album_info = get_album_info(album_id, access_token)
        if album_info:
            albums_data.append(album_info)

    for artist_id in artist_ids:
        artist_info = get_artist_info(artist_id, access_token)
        if artist_info:
            artists_data.append(artist_info)

    # Create the database and save data
    connection = create_database()
    save_albums_to_database(albums_data, connection)
    save_artists_to_database(artists_data, connection)

    # Close the connection
    connection.close()
    print("Data saved to database successfully!")

if __name__ == "__main__":
    main()
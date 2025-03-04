import sqlite3
import pandas as pd
import os
import json
import logging
from spotify_api import get_access_token, get_album_info, get_artist_info, extract_album_data_to_df, extract_artist_data_to_df


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

    with open('spotify_db/schema/create_album_schema.sql', 'r') as file:
        create_album_table_query = file.read()
    cursor.execute(create_album_table_query)

    with open('spotify_db/schema/create_artist_schema.sql', 'r') as file:
        create_artist_table_query = file.read()
    cursor.execute(create_artist_table_query)

    connection.commit()
    return connection

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    access_token = get_access_token()
        
    album_ids = read_ids_from_txt('album_ids.txt')
    artist_ids = read_ids_from_txt('artist_ids.txt')

    albums_df = extract_album_data_to_df(album_ids, access_token)
    artists_df = extract_artist_data_to_df(artist_ids, access_token)
    
    connection = create_database()
    albums_df.to_sql('albums', connection, if_exists='replace', index=False)
    artists_df.to_sql('artists', connection, if_exists='replace', index=False)

    connection.close()
    logging.info("Data saved to database successfully!")

if __name__ == "__main__":
    main()
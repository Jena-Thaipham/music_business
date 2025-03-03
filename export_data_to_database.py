import sqlite3
import pandas as pd
import os
import json
import logging
from spotify_api import get_access_token, get_album_info, get_artist_info, extract_album_data_to_df, extract_artist_data_to_df
from file_utils import read_ids_from_txt, create_database  

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

import sqlite3

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
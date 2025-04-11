import sqlite3
import logging
import pandas as pd
from typing import Dict
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path: str = "spotify_db/spotify.db", schema_dir: str = "spotify_db/schema"):
        self.db_path = db_path
        self.schema_dir = schema_dir
        self.connection = None
        self._initialize_database()

    def _load_schema_file(self, filename: str) -> str:
        schema_path = Path(self.schema_dir) / filename
        with open(schema_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _initialize_database(self):
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
            sql = self._load_schema_file(schema_file)
            cursor.executescript(sql)

        self.connection.commit()

    def save_data(self, dataframes: Dict[str, pd.DataFrame]) -> bool:
        if not self.connection:
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
                    data_tuples = [tuple(x) for x in df.to_numpy()]
                    cursor.executemany(sql, data_tuples)

            self.connection.commit()
            return True
        except Exception:
            self.connection.rollback()
            return False

    def close(self):
        if self.connection:
            self.connection.close()

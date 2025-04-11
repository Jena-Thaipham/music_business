import logging
import pandas as pd
from typing import List, Dict
from SpotifyExtractor import SpotifyExtractor
from DatabaseManager import DatabaseManager  

class SpotifyETLPipeline:
    def __init__(self):
        self.extractor = SpotifyExtractor()
        self.access_token = self.extractor.get_access_token()
        self.db_manager = DatabaseManager()

    def _read_ids(self, file_path: str) -> List[str]:
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.warning(f"ID file not found: {file_path}")
            return []

    def _extract_data(self) -> Dict[str, pd.DataFrame]:
        album_ids = self._read_ids('album_ids.txt')
        artist_ids = self._read_ids('artist_ids.txt')
        track_ids = self._read_ids('track_ids.txt')
        playlist_ids = self._read_ids('playlist_ids.txt')

        albums_df = pd.DataFrame(filter(None, [self.extractor.get_album_info(aid) for aid in album_ids]))
        artists_df = pd.DataFrame(filter(None, [self.extractor.get_artist_info(aid) for aid in artist_ids]))
        tracks_df = pd.DataFrame(filter(None, [self.extractor.get_track_info(tid) for tid in track_ids]))

        playlists = []
        playlist_tracks = []

        for pid in playlist_ids:
            playlist_info = self.extractor.get_playlist_info(pid)
            if playlist_info:
                playlists.append(playlist_info)
            tracks_info = self.extractor.get_playlist_tracks(pid)
            if tracks_info:
                playlist_tracks.extend(tracks_info)

        playlists_df = pd.DataFrame(playlists)
        playlist_tracks_df = pd.DataFrame(playlist_tracks)

        return {
            'albums': albums_df,
            'artists': artists_df,
            'tracks': tracks_df,
            'playlists': playlists_df,
            'playlist_tracks': playlist_tracks_df
        }

    def run(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        dataframes = self._extract_data()
        self.db_manager.save_data(dataframes)
        self.db_manager.close()
        logging.info("ETL pipeline completed and data saved to database.")

if __name__ == "__main__":
    pipeline = SpotifyETLPipeline()
    pipeline.run()

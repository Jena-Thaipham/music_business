import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Define functions to fetch data
def get_tracks_from_playlist(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def get_audio_features(sp, track_ids):
    features = sp.audio_features(track_ids)
    return features

def get_artist_info(sp, artist_id):
    artist = sp.artist(artist_id)
    return artist

def get_album_info(sp, album_id):
    album = sp.album(album_id)
    return album

def get_top_tracks(sp, artist_id):
    top_tracks = sp.artist_top_tracks(artist_id)
    return top_tracks['tracks']

def get_related_artists(sp, artist_id):
    related_artists = sp.artist_related_artists(artist_id)
    return related_artists['artists']

def get_genres(sp):
    genres = sp.recommendation_genre_seeds()
    return genres['genres']

def get_markets(sp):
    markets = sp.markets()
    return markets['markets']

def get_playlists(sp, user_id):
    playlists = sp.user_playlists(user_id)
    return playlists['items']

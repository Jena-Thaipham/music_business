from spotify_api import get_access_token, get_album_info, get_artist_info
from file_utils import read_ids_from_txt, save_to_csv

def main():
    access_token = get_access_token()
    if not access_token:
        print("Failed to get access token.")
        return

    album_ids = read_ids_from_txt('album_ids.txt')
    artist_ids = read_ids_from_txt('artist_ids.txt')

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

    save_to_csv(albums_data, 'albums.csv')
    save_to_csv(artists_data, 'artists.csv')
    print("Data saved to albums.csv and artists.csv!")

if __name__ == "__main__":
    main()
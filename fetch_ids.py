import requests
import base64
import random
import logging
from dotenv import load_dotenv
import os
import time

def get_access_token():
    load_dotenv()
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}",
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        logging.error(f"Error: {response.status_code} - {response.text}")
        return None

def fetch_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  
                retry_after = int(response.headers.get('Retry-After', 5))
                logging.warning(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            else:
                logging.error(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)  
    return None

def get_random_ids(access_token, item_type, count=40):
    base_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    search_terms = [
        '%25a%25', '%25b%25', '%25c%25', '%25d%25', '%25e%25', 
        '%25f%25', '%25g%25', '%25h%25', '%25i%25', '%25j%25',
        '%25k%25', '%25l%25', '%25m%25', '%25n%25', '%25o%25',
        '%25p%25', '%25q%25', '%25r%25', '%25s%25', '%25t%25',
        '%25u%25', '%25v%25', '%25w%25', '%25x%25', '%25y%25', '%25z%25',
        '%25the%25', '%25and%25', '%25you%25', '%25that%25', '%25have%25',
        '%25for%25', '%25with%25', '%25this%25', '%25from%25', '%25they%25',
        '%25music%25', '%25song%25', '%25tune%25', '%25beat%25', '%25melody%25',
        '%25rhythm%25', '%25sound%25', '%25track%25', '%25album%25', '%25artist%25',
        '%25band%25', '%25singer%25', '%25vocal%25', '%25lyric%25', '%25chord%25',
        '%25pop%25', '%25rock%25', '%25jazz%25', '%25blues%25', '%25hiphop%25',
        '%25rap%25', '%25edm%25', '%25electronic%25', '%25classical%25', '%25country%25',
        '%25rnb%25', '%25reggae%25', '%25metal%25', '%25punk%25', '%25indie%25',
        '%25happy%25', '%25sad%25', '%25love%25', '%25heart%25', '%25cool%25',
        '%25hot%25', '%25chill%25', '%25party%25', '%25dance%25', '%25sleep%25',
        '%25energy%25', '%25calm%25', '%25romantic%25', '%25summer%25', '%25winter%25',
        '%25mix%25', '%25best%25', '%25top%25', '%25great%25', '%25awesome%25',
        '%25hit%25', '%25now%25', '%25new%25', '%25old%25', '%25gold%25',
        '%25fm%25', '%25radio%25', '%25live%25', '%25cover%25', '%25remix%25',
        '%252023%25', '%252022%25', '%252021%25', '%252020%25', '%2519%25',
        '%2590s%25', '%2580s%25', '%2570s%25', '%2560s%25', '%2550s%25',
        '%25usa%25', '%25uk%25', '%25europe%25', '%25asia%25', '%25africa%25',
        '%25latin%25', '%25kpop%25', '%25jpop%25', '%25french%25', '%25german%25'
    ]

    random.shuffle(search_terms)

    ids = set()
    for term in search_terms:
        if len(ids) >= count:
            break

        url = f"{base_url}?q={term}&type={item_type}&limit=50"
        response = fetch_with_retry(url, headers)

        if response and response.status_code == 200:
            items = response.json().get(f"{item_type}s", {}).get("items", [])
            for item in items:
                if item and 'id' in item:
                    ids.add(item['id'])

        time.sleep(0.5)

    return random.sample(list(ids), min(count, len(ids))) if ids else []

def save_ids_to_file(ids, filename):
    existing_ids = set()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_ids = set(line.strip() for line in file.readlines())

    new_ids = set(ids) - existing_ids

    with open(filename, 'a') as file:
        for id in new_ids:
            file.write(f"{id}\n")

    return len(new_ids)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    access_token = get_access_token()

    if not access_token:
        logging.error("Failed to get access token. Exiting.")
        return

    album_count = save_ids_to_file(get_random_ids(access_token, 'album', 50), 'album_ids.txt')
    artist_count = save_ids_to_file(get_random_ids(access_token, 'artist', 50), 'artist_ids.txt')
    track_count = save_ids_to_file(get_random_ids(access_token, 'track', 50), 'track_ids.txt')
    playlist_count = save_ids_to_file(get_random_ids(access_token, 'playlist', 50), 'playlist_ids.txt')

    logging.info(f"Added {album_count} new albums, {artist_count} new artists, "
                 f"{track_count} new tracks, {playlist_count} new playlists to files.")

if __name__ == "__main__":
    main()

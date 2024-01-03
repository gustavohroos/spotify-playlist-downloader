from pytube import YouTube
import subprocess
import requests
import argparse
import logging
import time
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def authorization():
    token_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    token_data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    try:
        r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
        r.raise_for_status()
        token = r.json()["access_token"]
        return token
    except requests.RequestException as e:
        logging.error(f"Error during authorization: {e}")
        return None

def download_track(track, playlist_name):
    track_name, artist_name = track.split(' --- ')
    search_query = f"{track_name} {artist_name} lyrics"
    search_url = f"https://www.youtube.com/results?search_query={search_query}"
    if os.path.exists(f'{playlist_name}/{track_name}.mp4') or os.path.exists(f'{playlist_name}/{track_name}.mp3'):
        logging.info(f"{track_name} by {artist_name} already downloaded")
        return
    
    try:
        search_results = requests.get(search_url)
        search_results.raise_for_status()

        video_id = None
        for line in search_results.text.split('\n'):
            if 'watch?v=' in line:
                video_id = line.split('watch?v=')[1].split('"')[0]
                break

        if video_id:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            yt = YouTube(video_url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

            if stream:
                stream.download(output_path=f'./{playlist_name}/', filename=f'{track_name}.mp4')
                logging.info(f"Downloaded {track_name} by {artist_name}")       
            else:
                logging.warning(f"No suitable stream found for {track_name} by {artist_name}")
        else:
            logging.warning(f"No video found for {track_name} by {artist_name}")
    except requests.RequestException as e:
        logging.error(f"Error during download: {e}")

def convert_to_mp3(music, playlist_name):
    try:
        if not os.path.exists(f'{playlist_name}/{music[:-4]}.mp3'):
            subprocess.call(['ffmpeg', '-i', f'{playlist_name}/{music}', '-vn', '-ar', '44100', '-ac', '2', '-ab', '192k', '-f', 'mp3', f'{playlist_name}/{music[:-4]}.mp3'])
            os.remove(f'{playlist_name}/{music}')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during conversion: {e}")

def get_all_tracks(token, playlist_id, total_tracks):
    all_tracks = []
    offset = 0
    limit = 20

    while offset < total_tracks:
        user_params = {
            "market": "BR",
            "fields": "name,items(track(name, artists(name)))",
            "limit": limit,
            "offset": offset
        }

        user_headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }

        try:
            playlist_data = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", params=user_params, headers=user_headers)
            playlist_data.raise_for_status()

            playlist_data = playlist_data.json()

            playlist_tracks = playlist_data['items']
            all_tracks.extend([f"{track['track']['name']} --- {track['track']['artists'][0]['name']}" \
                               for track in playlist_tracks])
            offset += len(playlist_tracks)
        except requests.RequestException as e:
            logging.error(f"Error fetching playlist data: {e}")
            break

    assert len(all_tracks) == total_tracks
    all_tracks.sort()
    all_tracks = [track.replace('/', '') for track in all_tracks]
    logging.info(f"Found {len(all_tracks)} tracks")
    return all_tracks

def main(spotify_url):

    start = time.time()
    token = authorization()

    if token:
        playlist_id = spotify_url.split('/')[-1].split('?')[0]

        try:
            playlist_data = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/", headers={"Authorization": "Bearer " + token}).json()
            playlist_name = playlist_data['name']
            total_tracks = playlist_data['tracks']['total']
            all_tracks = get_all_tracks(token, playlist_id, total_tracks)

            if not os.path.exists(playlist_name):
                os.mkdir(playlist_name)

            for track in all_tracks:
                download_track(track, playlist_name)

            for music in os.listdir(playlist_name):
                convert_to_mp3(music, playlist_name)

            logging.info(f"Finished in {time.time() - start} seconds")
        except requests.RequestException as e:
            logging.error(f"Error fetching playlist data: {e}")
    else:
        logging.error("Authorization failed. Exiting.")

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('--url', type=str, help='Spotify playlist url')
    args = args.parse_args()
    if args.url:
        spotify_url = args.url
    else: 
        print("No url provided")
        exit()
    main(spotify_url)
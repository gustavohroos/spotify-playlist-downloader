# Spotify Playlist Downloader

This Python program allows you to download tracks from a Spotify playlist by searching for their lyrics on YouTube and converting the videos to MP3 format.

## Prerequisites

Before running the program, ensure you have the following:

- [Python](https://www.python.org/)
- [ffmpeg](https://www.ffmpeg.org/) (Make sure it's in your system's PATH)
- Install the required Python libraries:

  ```bash
  pip install pytube requests python-dotenv
  ```

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/spotify-playlist-downloader.git
   ```

2. Obtain Spotify API credentials:

   - Create a Spotify Developer account and create a new app.
   - Set the app's redirect URI to http://localhost:8888/callback.
   - Note the Client ID and Client Secret.

3. Create a `.env` file in the project directory and add your Spotify API credentials:

   ```ini
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

## Usage

Run the program using the following command:

```bash
python spotify_downloader.py --url <SPOTIFY_PLAYLIST_URL>
```

Replace <SPOTIFY_PLAYLIST_URL> with the URL of the Spotify playlist you want to download.

## Notes

- The program uses the YouTube API through the pytube library to search for videos based on track names and artists.
- The downloaded videos are saved in the specified playlist directory.
- The videos are then converted to MP3 format using ffmpeg.
- The program checks for duplicates, so previously downloaded tracks are skipped.
- Ensure that the ffmpeg executable is in your system's PATH.

## Disclaimer

This program is for educational purposes only. Respect the terms of service of both Spotify and YouTube, and only use this program for personal, non-commercial use.

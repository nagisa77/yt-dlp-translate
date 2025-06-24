# YouTube Playlist Downloader

This project automates two steps of my personal workflow:

1. Create or locate a playlist on YouTube through the YouTube Data API and list all its video URLs.
2. Download each video together with its English subtitles using [yt-dlp](https://github.com/yt-dlp/yt-dlp).

The downloaded files are stored locally so they can later be translated to Chinese and played back on Apple TV.

## Setup

1. Install Python dependencies with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and edit it to point to your Google OAuth client secrets JSON.

```bash
cp .env.example .env
# then edit .env
```

3. Copy `config.yaml.example` to `config.yaml` and edit it:
```bash
cp config.yaml.example config.yaml
```

4. Adjust `config.yaml` to define the playlist name, output directory and download options. If
   YouTube requests a sign-in to confirm you're not a bot, export your browser cookies and set
   `cookie_file` or `cookies_from_browser` under the `download` section to let yt-dlp authenticate.

5. Run the helper:

```bash
python main.py
```

OAuth authentication is required on first run. Afterwards the script will print the playlist URL, list the videos found and download each one with subtitles.

## Obtaining `client_secrets.json`

1. Sign in to [Google Cloud Console](https://console.cloud.google.com) and create a project.
2. Configure the consent screen in **APIs & Services → OAuth consent screen** and add test users if necessary.
3. Go to **APIs & Services → Credentials**, select **Create credentials → OAuth client ID**, choose the application type and fill in redirect URIs.
4. After creation, click **Download JSON** in the popup to save the file. Name it `client_secrets.json`, or set `GOOGLE_CLIENT_SECRETS_FILE` in `.env` to the correct path.
5. From April 2025 client secrets can only be downloaded at creation time, so regenerate them if lost.
6. Enable required Google APIs in **APIs & Services → Library**.

# YouTube Playlist Helper

This project provides a simple helper script for creating or locating a
YouTube playlist using the YouTube Data API. The playlist name is read
from `config.yaml` and OAuth credentials are configured via `.env`.

## Setup

1. Install Python dependencies with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and edit the values:

```bash
cp .env.example .env
# Edit .env to point to your OAuth client secrets JSON
```

3. Ensure `config.yaml` contains the playlist name you want to manage.

4. Run the helper:

```bash
python main.py
```

The script will open a browser for OAuth the first time it runs. After
authentication, it will print the URL of the playlist and list the URL
for each video currently in the playlist.

## How to getting client_secrets.json?

1. Sign in to [Google Cloud Console](https://console.cloud.google.com) and create a project.
2. Configure the consent screen in "APIs & Services → OAuth consent screen": choose Internal/External type, fill in app name and email, add test users for external flow.
3. Go to "APIs & Services → Credentials", select "Create credentials → OAuth client ID", choose application type (Desktop app, Web application etc.) and fill in redirect URIs.
4. After creation, click "Download JSON" in the popup to save the file, name it `client_secrets.json`, or set `GOOGLE_CLIENT_SECRETS_FILE` in `.env` to the actual path.
5. Starting April 2025, client secrets can only be downloaded at creation time, must be regenerated if lost.
6. Enable required Google APIs in "APIs & Services → Library".

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

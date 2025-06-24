import os
import pathlib
import logging
import yaml
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Read config
CONFIG_FILE = pathlib.Path('config.yaml')
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
else:
    config = {}

PLAYLIST_NAME = config.get('playlist_name', 'My playlist')

# Load .env
load_dotenv()
CLIENT_SECRETS_FILE = os.getenv('GOOGLE_CLIENT_SECRETS_FILE')
TOKEN_FILE = os.getenv('TOKEN_FILE', 'token.json')
SCOPES = ['https://www.googleapis.com/auth/youtube']

if not CLIENT_SECRETS_FILE:
    raise SystemExit('GOOGLE_CLIENT_SECRETS_FILE not set in .env')

creds = None
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
        token.write(creds.to_json())

# Build YouTube API client
youtube = build('youtube', 'v3', credentials=creds)

# Find or create playlist
try:
    playlists = youtube.playlists().list(part='snippet', mine=True, maxResults=50).execute()
except HttpError as e:
    raise SystemExit(f'Error fetching playlists: {e}')

playlist_id = None
for item in playlists.get('items', []):
    if item['snippet']['title'] == PLAYLIST_NAME:
        playlist_id = item['id']
        break

if not playlist_id:
    body = {
        'snippet': {
            'title': PLAYLIST_NAME,
            'description': 'Created by script'
        },
        'status': {
            'privacyStatus': 'private'
        }
    }
    try:
        response = youtube.playlists().insert(part='snippet,status', body=body).execute()
        playlist_id = response['id']
        logger.info('Created playlist %s', PLAYLIST_NAME)
    except HttpError as e:
        raise SystemExit(f'Error creating playlist: {e}')
else:
    logger.info('Found playlist %s', PLAYLIST_NAME)

playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'
logger.info('Playlist URL: %s', playlist_url)

# List all video URLs in the playlist
try:
    playlist_items = []
    page_token = None
    while True:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=page_token,
        )
        response = request.execute()
        playlist_items.extend(response.get('items', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break
except HttpError as e:
    raise SystemExit(f'Error fetching playlist items: {e}')

logger.info('Video URLs:')
for item in playlist_items:
    video_id = item['contentDetails']['videoId']
    logger.info('https://www.youtube.com/watch?v=%s', video_id)

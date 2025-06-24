import os
import logging
import yaml
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/youtube']

class YouTubePlaylist:
    def __init__(self, config: dict) -> None:
        self.playlist_name = config.get('playlist_name', 'My playlist')
        load_dotenv()
        client_secrets = os.getenv('GOOGLE_CLIENT_SECRETS_FILE')
        self.token_file = os.getenv('TOKEN_FILE', 'token.json')
        if not client_secrets:
            raise SystemExit('GOOGLE_CLIENT_SECRETS_FILE not set in .env')

        self.creds = None
        if os.path.exists(self.token_file):
            self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(self.token_file, 'w', encoding='utf-8') as token:
                token.write(self.creds.to_json())

        self.youtube = build('youtube', 'v3', credentials=self.creds)
        self.playlist_id = self._ensure_playlist()

    def _ensure_playlist(self) -> str:
        try:
            playlists = self.youtube.playlists().list(part='snippet', mine=True, maxResults=50).execute()
        except HttpError as e:
            raise SystemExit(f'Error fetching playlists: {e}')
        playlist_id = None
        for item in playlists.get('items', []):
            if item['snippet']['title'] == self.playlist_name:
                playlist_id = item['id']
                break
        if not playlist_id:
            body = {
                'snippet': {
                    'title': self.playlist_name,
                    'description': 'Created by script',
                },
                'status': {
                    'privacyStatus': 'private'
                }
            }
            try:
                response = self.youtube.playlists().insert(part='snippet,status', body=body).execute()
                playlist_id = response['id']
                logger.info('Created playlist %s', self.playlist_name)
            except HttpError as e:
                raise SystemExit(f'Error creating playlist: {e}')
        else:
            logger.info('Found playlist %s', self.playlist_name)
        logger.info('Playlist URL: https://www.youtube.com/playlist?list=%s', playlist_id)
        return playlist_id

    def video_urls(self):
        try:
            playlist_items = []
            page_token = None
            while True:
                request = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=self.playlist_id,
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

        for item in playlist_items:
            video_id = item['contentDetails']['videoId']
            yield f'https://www.youtube.com/watch?v={video_id}'

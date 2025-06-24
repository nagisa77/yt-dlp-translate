import logging
import pathlib
import yaml

from yt_helper import YouTubePlaylist, Downloader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

CONFIG_FILE = pathlib.Path('config.yaml')
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
else:
    config = {}

playlist = YouTubePlaylist(config)
urls = list(playlist.video_urls())
logger.info('Found %d videos in playlist', len(urls))

downloader = Downloader(config)
downloader.download(urls)

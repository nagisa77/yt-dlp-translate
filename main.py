import logging
import pathlib
import yaml

from yt_helper import YouTubePlaylist, Downloader, SubtitleTranslator
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

CONFIG_FILE = pathlib.Path('config.yaml')
assert CONFIG_FILE.exists(), 'config.yaml not found'
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# delete youtube_cookies.txt
if pathlib.Path('youtube_cookies.txt').exists():
    pathlib.Path('youtube_cookies.txt').unlink()

urls = config.get('video_urls')
if not urls:
    playlist = YouTubePlaylist(config)
    urls = list(playlist.video_urls())
    logger.info('Found %d videos in playlist', len(urls))

downloader = Downloader(config)
translator = SubtitleTranslator(config)

stop_event = threading.Event()
watcher = threading.Thread(
    target=translator.watch_directory,
    args=(downloader.output_path, stop_event),
    daemon=True,
)
watcher.start()

downloader.download(urls)

stop_event.set()
watcher.join()

translator.close()

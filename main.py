import logging
import pathlib
import yaml

from yt_helper import YouTubePlaylist, Downloader, SubtitleTranslator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

CONFIG_FILE = pathlib.Path('config.yaml')
assert CONFIG_FILE.exists(), 'config.yaml not found'
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

urls = config.get('video_urls')
if not urls:
    playlist = YouTubePlaylist(config)
    urls = list(playlist.video_urls())
    logger.info('Found %d videos in playlist', len(urls))

downloader = Downloader(config)
downloader.download(urls)

translator = SubtitleTranslator(config)
translator.translate_directory(downloader.output_path)

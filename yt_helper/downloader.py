import logging
from pathlib import Path
from typing import Iterable

from yt_dlp import YoutubeDL, parse_options

logger = logging.getLogger(__name__)

DEFAULT_OPTS = {
    'format': 'bestvideo+bestaudio/best',
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['en.*'],
    'subtitlesformat': 'srt',
    'outtmpl': '%(playlist)s/%(title)s.%(ext)s',
}

class Downloader:
    def __init__(self, config: dict) -> None:
        dl_config = config.get('download', {})
        trans_conf = config.get('translate', {})
        target_lang = trans_conf.get('target_lang', 'zh')

        self.output_path = Path(dl_config.get('output_path', 'downloads'))
        self.opts = DEFAULT_OPTS.copy()
        self.opts['format'] = dl_config.get('format', self.opts['format'])
        default_langs = [f'{target_lang}.*', 'en.*']
        self.opts['subtitleslangs'] = dl_config.get('subtitle_langs', default_langs)
        self.opts['outtmpl'] = str(self.output_path / '%(playlist)s/%(title)s.%(ext)s')
        browser = dl_config.get('cookies_from_browser')
        if browser:
            logger.info('Using cookies from browser %s', browser)
            self.opts['cookiefile'] = 'youtube_cookies.txt'
            if isinstance(browser, str):
                # Reuse yt-dlp's parser to handle KEYRING/PROFILE/CONTAINER syntax
                self.opts['cookiesfrombrowser'] = parse_options([
                    f'--cookies-from-browser={browser}'
                ])[1].cookiesfrombrowser
            else:
                # Allow passing tuples directly for advanced usage
                self.opts['cookiesfrombrowser'] = tuple(browser)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def download(self, urls: Iterable[str]):
        logger.info('Starting download of %d videos', len(list(urls)))
        # Re-generate iterable because we consumed it to count; easiest approach
        urls = list(urls)
        with YoutubeDL(self.opts) as ydl:
            for url in urls:
                try:
                    logger.info('Downloading %s', url)
                    ydl.download([url])
                except Exception as e:
                    logger.error('Failed to download %s: %s', url, e)



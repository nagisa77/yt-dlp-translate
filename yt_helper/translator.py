import logging
import os
from pathlib import Path
from typing import Iterable

import openai

logger = logging.getLogger(__name__)

class SubtitleTranslator:
    def __init__(self, config: dict) -> None:
        trans_conf = config.get('translate', {})
        self.target_lang = trans_conf.get('target_lang', 'zh')
        self.model = trans_conf.get('model', 'gpt-3.5-turbo')
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning('OPENAI_API_KEY not set; translation disabled')
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)

    def translate_directory(self, base: Path):
        if not self.client:
            return
        for srt in base.rglob('*.en*.srt'):
            target = srt.with_name(srt.name.replace('.en', f'.{self.target_lang}'))
            if target.exists():
                continue
            self.translate_file(srt, target)

    def translate_file(self, src: Path, dest: Path):
        logger.info('Translating %s -> %s', src, dest)
        content = src.read_text(encoding='utf-8')
        messages = [
            {
                'role': 'system',
                'content': f'Translate the following subtitles to {self.target_lang} and keep the SRT format.'
            },
            {'role': 'user', 'content': content},
        ]
        try:
            resp = self.client.chat.completions.create(model=self.model, messages=messages)
            translated = resp.choices[0].message.content
            dest.write_text(translated, encoding='utf-8')
        except Exception as e:
            logger.error('Failed to translate %s: %s', src, e)

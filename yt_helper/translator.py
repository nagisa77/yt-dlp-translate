import logging
import os
import re
from pathlib import Path
from typing import Iterable, Set

import openai

logger = logging.getLogger(__name__)

class SubtitleTranslator:
    def __init__(self, config: dict) -> None:
        trans_conf = config.get('translate', {})
        self.target_lang = trans_conf.get('target_lang', 'zh')
        self.model = trans_conf.get('model', 'gpt-4o-mini')
        # When True, translate even if subtitles in the target language already exist
        self.force = trans_conf.get('force', False)
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning('OPENAI_API_KEY not set; translation disabled')
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)

    def translate_directory(self, base: Path):
        if not self.client:
            return
        processed: Set[Path] = set()
        for srt in base.rglob('*.en*.srt'):
            # Remove the language suffix from the filename to determine the base
            base_name = re.sub(r'\.en[^.]*', '', srt.stem)
            base_path = srt.with_name(base_name)

            if base_path in processed:
                continue

            # Skip if any subtitle for the target language already exists
            existing = list(srt.parent.glob(f'{base_name}.{self.target_lang}*.srt'))
            if existing and not self.force:
                logger.info('Skipping %s because target subtitle already exists', srt)
                processed.add(base_path)
                continue

            target = srt.with_name(f'{base_name}.{self.target_lang}-ai.srt')
            self.translate_file(srt, target)
            processed.add(base_path)

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

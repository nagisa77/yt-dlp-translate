import logging
import os
import re
from pathlib import Path
from typing import Iterable, Set
import threading
import time

from tqdm import tqdm

import openai

logger = logging.getLogger(__name__)

class SubtitleTranslator:
    def __init__(self, config: dict) -> None:
        trans_conf = config.get('translate', {})
        self.target_lang = trans_conf.get('target_lang', 'zh')
        self.model = trans_conf.get('model', 'gpt-4o-mini')
        # When True, translate even if subtitles in the target language already exist
        self.force = trans_conf.get('force', False)
        self.entries_per_request = max(1, trans_conf.get('entries_per_request', 1))
        # Number of worker threads used for translating files
        self.threads = max(1, int(trans_conf.get('threads', 1)))
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning('OPENAI_API_KEY not set; translation disabled')
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=api_key)

    def translate_directory(self, base: Path):
        if not self.client:
            return

        # Collect unique subtitle files that require translation
        tasks = []
        processed: Set[Path] = set()
        for srt in base.rglob('*.en*.srt'):
            base_name = re.sub(r'\.en[^.]*', '', srt.stem)
            base_path = srt.with_name(base_name)
            if base_path in processed:
                continue

            existing = list(srt.parent.glob(f'{base_name}.{self.target_lang}*.srt'))
            if existing and not self.force:
                logger.info('Skipping %s because target subtitle already exists', srt)
                processed.add(base_path)
                continue

            target = srt.with_name(f'{base_name}.{self.target_lang}-ai.srt')
            tasks.append((srt, target))
            processed.add(base_path)

        total = len(tasks)
        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=self.threads) as ex, \
                tqdm(total=total, desc='Translating', unit='file') as pbar:
            futures = {
                ex.submit(self.translate_file, srt, target): (srt, target)
                for srt, target in tasks
            }
            for _ in as_completed(futures):
                pbar.update(1)

    def watch_directory(self, base: Path, stop_event: threading.Event, poll: float = 5.0) -> None:
        """Continuously translate subtitles in ``base`` until ``stop_event`` is set."""
        while not stop_event.is_set():
            self.translate_directory(base)
            # Wait for the next check or exit early if stopped
            stop_event.wait(poll)
        # Final pass after downloads finish
        self.translate_directory(base)

    def translate_file(self, src: Path, dest: Path):
        """Translate a single SRT file with per-entry progress reporting."""

        content = src.read_text(encoding="utf-8")

        # Split into subtitle blocks separated by blank lines
        entries: list[str] = []
        block: list[str] = []
        for line in content.splitlines():
            if line.strip() == "" and block:
                entries.append("\n".join(block))
                block = []
            else:
                block.append(line)
        if block:
            entries.append("\n".join(block))

        translated_entries: list[str] = []
        total = len(entries)

        with tqdm(total=total, desc=src.name, unit="entry") as pbar:
            batch: list[tuple[str, str, str]] = []

            def translate_segment(segment: list[tuple[str, str, str]]) -> list[str]:
                """Translate a sequence of subtitle entries, retrying with
                exponentially smaller segments on line count mismatch."""

                if not segment:
                    return []

                numbered = [f"[{i}] {text}" for i, (_, _, text) in enumerate(segment, 1)]
                system_msg = (
                    f"Translate every line to {self.target_lang}. "
                    "Keep the same numbering format like [1], [2], … and do NOT change order."
                )
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": "\n".join(numbered)},
                ]

                logger.info("Translating batch %s", "\n".join(numbered))

                translations_map: dict[int, str] = {}
                try:
                    resp = self.client.chat.completions.create(
                        model=self.model, messages=messages
                    )
                    raw = resp.choices[0].message.content.strip().splitlines()

                    pattern = re.compile(r"^\[(\d+)]\s*(.*)$")
                    for line in raw:
                        m = pattern.match(line)
                        if m:
                            translations_map[int(m.group(1))] = m.group(2)
                except Exception as e:
                    logger.error("Failed to translate part of %s: %s", src, e)

                if len(translations_map) != len(segment) and len(segment) > 1:
                    logger.warning(
                        "Mismatched line count; retrying with smaller batches: %d -> %d",
                        len(segment), len(segment) // 2 or 1,
                    )
                    mid = len(segment) // 2
                    return translate_segment(segment[:mid]) + translate_segment(segment[mid:])

                results = []
                for local_idx, (idx, timestamp, text) in enumerate(segment, 1):
                    trans = translations_map.get(local_idx, text)
                    results.append("\n".join([idx, timestamp, trans.strip()]))
                return results

            def process_batch() -> None:
                if not batch:
                    return

                translated_entries.extend(translate_segment(batch))
                pbar.update(len(batch))
                batch.clear()

            for entry in entries:
                lines = entry.splitlines()
                if len(lines) < 3:
                    process_batch()
                    translated_entries.append(entry)
                    pbar.update(1)
                    continue

                idx, timestamp, *text_lines = lines
                text = "\n".join(text_lines)

                batch.append((idx, timestamp, text))
                if len(batch) >= self.entries_per_request:
                    process_batch()

            process_batch()

        dest.write_text("\n\n".join(translated_entries) + "\n", encoding="utf-8")

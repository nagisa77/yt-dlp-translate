# 🔥YouTube Playlist Downloader & Translator

This project automates several tedious steps involved in archiving and
watching YouTube content offline. It can create or locate a playlist, download
every video with subtitles and then translate those subtitles into your
preferred language. The files are stored locally so they can be played back on
any device.

## Features

* **Playlist management** – Create or locate a playlist on YouTube through the
  Data API and retrieve every video URL. Alternatively, you can provide the list
  of video URLs directly in `config.yaml`.
* **Video and subtitle downloader** – Grab each video with
  [yt-dlp](https://github.com/yt-dlp/yt-dlp), fetching subtitles in your target
  language when available or falling back to English.
* **Automatic subtitle translation** – English subtitles are translated to the
  configured language using OpenAI, so you always end up with text you can
  understand.
* **Resume support** – Existing video files are detected and skipped, letting
  you rerun the script to download only what is missing.
* **Browser cookie authentication** – When YouTube requires a sign‑in, yt-dlp
  can reuse cookies from your browser so even age‑restricted videos are
  downloaded seamlessly.

## Setup

1. Install Python dependencies with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and edit it to point to your Google OAuth client secrets JSON. You can skip this step if `video_urls` is provided in the config.

```bash
cp .env.example .env
# then edit .env
```

3. Copy `config.yaml.example` to `config.yaml` and edit it:
```bash
cp config.yaml.example config.yaml
```

4. Adjust `config.yaml` to specify either `playlist_name` or a list of
   `video_urls` along with the output directory and download options.
   Useful settings include:
   - `cookies_from_browser` under `download` lets yt-dlp authenticate using your
     browser cookies when YouTube asks for a sign‑in. Extracted cookies are saved
     to `youtube_cookies.txt` for reuse.
   - `download.concurrent_fragment_downloads` sets the thread count for
     multi-threaded fragment downloads. Leave it unset to disable.
   - `translate.force` forces subtitle translation even if files already exist in
     the target language.
   - `translate.entries_per_request` batches multiple subtitle entries into one
     OpenAI request. When a batch yields fewer lines than expected, the
     translator halves the batch and retries until every line is translated or
     only single-line requests remain.
   - `translate.threads` defines how many subtitle files are translated in
     parallel.

5. Run the helper to download videos and subtitles:

```bash
python main.py
```

After the download finishes, the script automatically translates any English
subtitles to the configured target language using your OpenAI API key. The
translator runs in parallel with the downloader, so translation begins as soon
as matching ``*.en*.srt`` files appear in the output directory. It keeps
checking for new files until all downloads finish. The ``translate.force``
option still decides whether to retranslate existing subtitles.

OAuth authentication is required on first run when using `playlist_name`. If
`video_urls` are provided, the script skips Google login. After authentication
the script prints the playlist URL (if any), lists the videos found and
downloads each one with subtitles.

## Obtaining client_secrets.json file

**Note:** Obtaining the `client_secrets.json` file is only required when using `playlist_name` to access YouTube playlists. If you're only downloading individual videos using `video_urls`, you can skip this step.

The following steps are only required when using `playlist_name` to access the YouTube Data API.

1. Sign in to [Google Cloud Console](https://console.cloud.google.com) and create a project.
2. Configure the consent screen in **APIs & Services → OAuth consent screen** and add test users if necessary.
3. Go to **APIs & Services → Credentials**, select **Create credentials → OAuth client ID**, choose the application type and fill in redirect URIs.
4. After creation, click **Download JSON** in the popup to save the file. Name it `client_secrets.json`, or set `GOOGLE_CLIENT_SECRETS_FILE` in `.env` to the correct path.
5. From April 2025 client secrets can only be downloaded at creation time, so regenerate them if lost.
6. Enable required Google APIs in **APIs & Services → Library**.

## License

This project is licensed under the [MIT](LICENSE) license.

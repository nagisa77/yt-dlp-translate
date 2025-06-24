# YouTube Playlist Helper

This project provides a simple helper script for creating or locating a
YouTube playlist using the YouTube Data API. The playlist name is read
from `config.yaml` and OAuth credentials are configured via `.env`.

## Setup

1. Install Python dependencies with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and edit the values:

```bash
cp .env.example .env
# Edit .env to point to your OAuth client secrets JSON
```

3. Ensure `config.yaml` contains the playlist name you want to manage.

4. Run the helper:

```bash
python main.py
```

The script will open a browser for OAuth the first time it runs. After
authentication, it will print the URL of the playlist.

## 获取 client_secrets.json

1. 登录 [Google Cloud Console](https://console.cloud.google.com) 并创建项目。
2. 在 “APIs & Services → OAuth consent screen” 配置同意屏幕：选择内部/外部类型，填写应用名和邮箱，外部流程需添加测试用户。
3. 打开 “APIs & Services → Credentials”，选择 “Create credentials → OAuth client ID”，按需选择应用类型（Desktop app、Web application 等），并填写重定向 URI。
4. 创建完成后在弹窗点击 “Download JSON” 保存文件，将其命名为 `client_secrets.json`，或在 `.env` 中设置 `GOOGLE_CLIENT_SECRETS_FILE` 为实际路径。
5. 2025 年 4 月起 client secret 仅在创建时可下载，丢失后需重新生成。
6. 在 “APIs & Services → Library” 中启用要调用的 Google API。

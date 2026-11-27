# YouTube Downloader (Local)

A private, locally-hosted web app that downloads YouTube videos as MP4 (360p/720p) or audio as MP3.

Built with FastAPI, yt-dlp, and FFmpeg. Runs entirely on your machine — no external server, no third-party API.

## Features
- Clean web UI at `http://localhost:8000`
- 360p MP4 (small, fast — no FFmpeg needed)
- 720p MP4 (HD, merged with FFmpeg)
- MP3 audio extraction at 192kbps
- Handles YouTube's current JS challenge via Deno

## Setup

1. Install Python 3.10+
2. Install FFmpeg and Deno:
   - Windows: `winget install -e --id yt-dlp.FFmpeg` and `winget install --id=DenoLand.Deno`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
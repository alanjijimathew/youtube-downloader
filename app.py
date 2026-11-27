import sys, uuid, subprocess
import yt_dlp
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()
DOWNLOAD_DIR = Path("./downloads").resolve()
DOWNLOAD_DIR.mkdir(exist_ok=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>My Downloader</title>
  <style>
    body { font-family: sans-serif; max-width: 620px; margin: 3rem auto; padding: 0 1rem; background: #fafafa; }
    h1 { margin-bottom: 0.25rem; }
    .sub { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
    input, select, button { width: 100%; padding: 0.7rem; margin: 0.4rem 0; box-sizing: border-box; font-size: 1rem; border-radius: 6px; border: 1px solid #ccc; }
    button { background: #2563eb; color: white; border: none; cursor: pointer; font-weight: 600; }
    button:disabled { background: #94a3b8; cursor: wait; }
    #status { margin-top: 1rem; padding: 1rem; background: white; border-radius: 6px; border: 1px solid #ddd; min-height: 1.5rem; white-space: pre-wrap; font-family: monospace; font-size: 0.85rem; }
    .dl { display: block; margin-top: 1rem; padding: 0.9rem; background: #dcfce7; text-align: center; border-radius: 6px; text-decoration: none; color: #166534; font-weight: 600; }
  </style>
</head>
<body>
  <h1>My Downloader</h1>
  <div class="sub">Private local tool — personal use only.</div>
  <input id="url" placeholder="Paste a YouTube link here...">
  <select id="quality">
    <option value="360p">MP4 — 360p (small, fast)</option>
    <option value="720p">MP4 — 720p (HD)</option>
    <option value="mp3">MP3 — audio only (192kbps)</option>
  </select>
  <button id="btn" onclick="go()">Download</button>
  <div id="status">Ready.</div>
  <div id="out"></div>

  <script>
    async function go() {
      const url = document.getElementById('url').value.trim();
      const quality = document.getElementById('quality').value;
      const btn = document.getElementById('btn');
      const status = document.getElementById('status');
      const out = document.getElementById('out');

      if (!url) { status.textContent = 'Paste a link first.'; return; }

      btn.disabled = true;
      out.innerHTML = '';
      status.textContent = 'Downloading... this can take 10-60 seconds.';

      try {
        const r = await fetch('/download', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({url, quality})
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || 'Failed');

        status.textContent = 'Done!';
        const a = document.createElement('a');
        a.href = '/file/' + encodeURIComponent(data.filename);
        a.className = 'dl';
        a.textContent = 'Download: ' + data.filename;
        a.setAttribute('download', '');
        out.appendChild(a);
      } catch (e) {
        status.textContent = 'Error: ' + e.message;
      } finally {
        btn.disabled = false;
      }
    }
  </script>
</body>
</html>
"""

class Req(BaseModel):
    url: str
    quality: str

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.post("/download")
def download(req: Req):
    if "youtube.com" not in req.url and "youtu.be" not in req.url:
        raise HTTPException(400, "Please provide a valid YouTube link.")

    before = set(DOWNLOAD_DIR.iterdir())
    outtmpl = str(DOWNLOAD_DIR / "%(title).60s.%(ext)s")

    ydl_opts = {
        'outtmpl': outtmpl,
        'noplaylist': True,
        'remote_components': ['ejs:github'],
        'force_ipv4': True,
        'verbose': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['web_embedded', 'default', '-web_embedded']
            }
        },
    }

    if req.quality == "mp3":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif req.quality == "720p":
        ydl_opts['format'] = 'bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/18'
        ydl_opts['merge_output_format'] = 'mp4'
    else:
        ydl_opts['format'] = '18'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([req.url])
    except Exception as e:
        raise HTTPException(500, str(e))

    new = set(DOWNLOAD_DIR.iterdir()) - before
    if not new:
        raise HTTPException(500, "yt-dlp finished but no new file appeared.")
    newest = max(new, key=lambda f: f.stat().st_mtime)
    return {"filename": newest.name}

@app.get("/file/{filename}")
def get_file(filename: str):
    path = DOWNLOAD_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "File not found.")
    return FileResponse(path, filename=filename)

if __name__ == "__main__":
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
VidSnap Backend Server
─────────────────────────────────────────
Fetches real video info (title, thumbnail, formats)
and serves downloads for YouTube, TikTok, Instagram, etc.

SETUP:
  pip install yt-dlp flask flask-cors

RUN:
  python app.py

Server runs at: http://localhost:5000
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import re

app = Flask(__name__)
CORS(app)  # Allows your website (any domain) to call this server


def human_size(bytes_num):
    """Convert bytes to readable size like '480 MB'"""
    if not bytes_num:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_num < 1024:
            return f"{bytes_num:.0f} {unit}"
        bytes_num /= 1024
    return f"{bytes_num:.1f} TB"


def human_duration(seconds):
    """Convert seconds to '12:34' format"""
    if not seconds:
        return "0:00"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


@app.route('/api/info', methods=['POST'])
def get_info():
    """
    Takes a video URL, returns title, thumbnail, duration,
    and a clean list of downloadable formats.
    """
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,  # Just fetch info, don't download yet
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Build a clean format list (dedupe by resolution)
        formats = []
        seen_quality = set()

        for f in info.get('formats', []):
            height = f.get('height')
            ext = f.get('ext')
            filesize = f.get('filesize') or f.get('filesize_approx')

            # VIDEO formats (has video + audio, or video-only that we can label)
            if f.get('vcodec') != 'none' and height:
                label = f"{height}p"
                if label in seen_quality:
                    continue
                seen_quality.add(label)
                formats.append({
                    "type": "video",
                    "quality": label,
                    "ext": ext,
                    "size": human_size(filesize),
                    "format_id": f.get('format_id'),
                    "url": f.get('url')  # Direct download link
                })

        # AUDIO-only formats
        audio_formats = [f for f in info.get('formats', [])
                          if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
        if audio_formats:
            best_audio = max(audio_formats, key=lambda f: f.get('abr') or 0)
            formats.append({
                "type": "audio",
                "quality": f"{int(best_audio.get('abr') or 128)}kbps",
                "ext": best_audio.get('ext'),
                "size": human_size(best_audio.get('filesize') or best_audio.get('filesize_approx')),
                "format_id": best_audio.get('format_id'),
                "url": best_audio.get('url')
            })

        # Sort video formats by quality, highest first
        formats.sort(key=lambda f: (f['type'] != 'video', -int(re.sub(r'\D', '', f['quality']) or 0)))

        result = {
            "title": info.get('title', 'Unknown Title'),
            "platform": info.get('extractor_key', 'Unknown'),
            "duration": human_duration(info.get('duration')),
            "views": info.get('view_count', 0),
            "thumbnail": info.get('thumbnail', ''),
            "formats": formats
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Could not fetch video info: {str(e)}"}), 500


@app.route('/api/download', methods=['GET'])
def download():
    """
    Streams the actual video/audio file to the user's browser.
    Usage: /api/download?url=<video_url>&format_id=<id>
    """
    url = request.args.get('url')
    format_id = request.args.get('format_id', 'best')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'format': format_id,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info.get('url')
            title = re.sub(r'[^\w\s-]', '', info.get('title', 'video'))
            ext = info.get('ext', 'mp4')

        # Redirect the browser straight to the real file URL (fast, no server storage needed)
        import requests
        r = requests.get(direct_url, stream=True)
        return Response(
            r.iter_content(chunk_size=8192),
            content_type=r.headers.get('content-type', 'video/mp4'),
            headers={
                "Content-Disposition": f'attachment; filename="{title}.{ext}"'
            }
        )
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "VidSnap backend is running ✅"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

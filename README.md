# VidSnap — Reels/TikTok/Shorts Downloader

A fast, free, single-page web tool for downloading HD video and audio from
Instagram Reels, TikTok, YouTube Shorts, Facebook, Twitter/X, Pinterest and
50+ other platforms.

## 🚀 Live Demo
Once deployed, your live link will appear here, e.g.:
`https://yourusername.github.io/vidsnap`

## 📁 Project Structure
```
index.html      → the entire website (HTML + CSS + JS in one file)
```

## ✨ Features
- Paste multiple links at once (one per line) — all process in parallel
- Per-link result cards with title, thumbnail, duration, view count
- Video quality selector (4K / 1080p / 720p / 480p) and audio-only (MP3/M4A)
- "Download All" button for batch downloads
- Built-in ad slots (Google AdSense ready)
- SEO optimized — meta tags, Open Graph, JSON-LD structured data
- Fully responsive, light theme

## ⚠️ Current Status: Frontend Demo
This repo currently contains the **frontend only**. The download/analyze
buttons simulate results with placeholder data so the UI/UX can be tested
end-to-end.

To make it fetch **real** video data, you need a small backend:

```bash
pip install yt-dlp flask flask-cors
```

See `app.py` (in a separate backend repo, deployed to Railway/Render — NOT
GitHub Pages, since GitHub Pages only serves static files and cannot run
Python). Once your backend is live, update the `fetchVideoInfo()` function
inside `index.html` to call your real API endpoint instead of the mock data.

## 🌐 Deployment
This is a static site — it can be deployed instantly to:
- **GitHub Pages** (free, see below)
- Vercel / Netlify / Cloudflare Pages (also free, drag-and-drop)

## 📄 License
MIT — free to use, modify, and deploy.

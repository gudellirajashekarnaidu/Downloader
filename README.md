# Downloder (version A)

Paste a link, download the video as MP4 or extract the audio as MP3.
No accounts, no database. Light, Samsung Digital Wellbeing-style interface.

## Run it

You need Python 3.11+, Node 18+, and FFmpeg on your PATH.

```bash
# 1. Backend (http://127.0.0.1:8000)
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Frontend (http://localhost:5173), in a second terminal
cd frontend
npm install
npm run dev
```

Run the backend tests with `python -m unittest discover -s tests -t .` from the `backend` folder.

## What it supports

| Link type | How it's handled |
| --- | --- |
| Direct media links (.mp4, .webm, .mp3 ...) | Downloaded as the original file. Audio is extracted with FFmpeg. |
| Public Instagram, X, Telegram posts | yt-dlp, public media only. No logins or cookies. |
| Anything else | A clear "not supported" message. |

Whether a platform link works depends on the platform. They change their sites
often, so keep yt-dlp updated (`pip install -U yt-dlp`) and expect some links to fail.
YouTube is left out on purpose because its terms don't allow downloads outside its own
features. Platforms are listed in `backend/app/config.py`.

## How it fits together

```
backend/app/
  security.py    URL checks and SSRF protection (every link goes through this first)
  direct.py      direct media links, redirects re-validated at every hop
  extractors.py  public posts through yt-dlp, restricted to the platforms in config.py
  media.py       FFmpeg audio extraction
  service.py     analyze a link, run download jobs, delete files after 30 minutes
  main.py        API: /api/analyze, /api/jobs, /api/jobs/{id}, /api/jobs/{id}/file
frontend/src/
  App.jsx        page state and polling
  components/    URL card, result, options, progress ring, supported links
```

## Before you put it online

- Add an egress firewall that blocks private IP ranges. `security.py` explains why.
- Serve the frontend and API from one domain, or set `VITE_API_BASE` and `DOWNLODER_CORS`.
- The job list and rate limiter live in memory, so run a single server process.
- Add a terms page and a takedown contact. People will paste links to content they don't own.

## Next steps

Version B adds accounts (JWT), MongoDB for history, and an admin dashboard.
Version C swaps the in-memory job list in `service.py` for Redis + Celery and adds the React Native app.

"""Public posts from supported platforms, handled with yt-dlp.

Only public media is attempted: no cookies, no logins. If a platform asks for
a login or blocks the request, the user gets a plain explanation instead.
"""
from pathlib import Path

from . import config
from .media import ffmpeg_available


class Unsupported(Exception):
    """The post can't be downloaded. The message is safe to show to the user."""


PUBLIC_ONLY = (
    "We couldn't get this one. It may be private, need a login, or the platform may not allow "
    "downloads for it."
)


def _load():
    try:
        import yt_dlp
    except ImportError:
        raise Unsupported("Platform links aren't available because yt-dlp isn't installed on the server.")
    return yt_dlp


def _options(**extra) -> dict:
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": config.REQUEST_TIMEOUT,
        "max_filesize": config.MAX_FILE_BYTES,
        "restrictfilenames": True,
        **extra,
    }


def analyze(url: str) -> dict:
    yt_dlp = _load()
    try:
        with yt_dlp.YoutubeDL(_options()) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError:
        raise Unsupported(PUBLIC_ONLY)

    if info.get("_type") == "playlist":
        entries = [e for e in (info.get("entries") or []) if e]
        if not entries:
            raise Unsupported(PUBLIC_ONLY)
        info = entries[0]

    formats = info.get("formats") or []
    heights = sorted(
        {f["height"] for f in formats if f.get("height") and f.get("vcodec") not in (None, "none")},
        reverse=True,
    )
    has_video = bool(heights) or bool(info.get("url"))
    return {
        "title": info.get("title") or "Untitled",
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "uploader": info.get("uploader"),
        "qualities": heights,
        "can_video": has_video,
        "can_audio": has_video and ffmpeg_available(),
    }


def download(url: str, kind: str, quality: str | None, dest_dir: Path, on_progress) -> Path:
    yt_dlp = _load()

    def hook(status: dict) -> None:
        if status.get("status") == "downloading":
            total = status.get("total_bytes") or status.get("total_bytes_estimate")
            if total:
                on_progress(min(status.get("downloaded_bytes", 0) / total, 1.0) * 0.9)
        elif status.get("status") == "finished":
            on_progress(0.9)

    if kind == "audio":
        opts = _options(
            format="bestaudio/best",
            postprocessors=[{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        )
    else:
        if quality and quality.isdigit():
            fmt = f"bv*[height<={quality}]+ba/b[height<={quality}]/b"
        else:
            fmt = "bv*+ba/b"
        opts = _options(format=fmt, merge_output_format="mp4")

    opts.update(
        outtmpl=str(dest_dir / "%(title).80s.%(ext)s"),
        progress_hooks=[hook],
    )

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError:
        raise Unsupported(PUBLIC_ONLY)

    files = [p for p in dest_dir.iterdir() if p.is_file() and p.suffix not in (".part", ".ytdl")]
    if not files:
        raise Unsupported(PUBLIC_ONLY)
    return max(files, key=lambda p: p.stat().st_size)

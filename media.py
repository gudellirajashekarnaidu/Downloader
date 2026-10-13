"""FFmpeg helpers (standard library only)."""
import re
import shutil
import subprocess
from pathlib import Path


class MediaError(RuntimeError):
    """Processing failed. The message is safe to show to the user."""


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def safe_stem(name: str, fallback: str = "media") -> str:
    """File name without extension, reduced to characters that are safe everywhere."""
    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem).strip(" ._-")
    return stem[:80] or fallback


def extract_mp3(source: Path, bitrate: str = "192k") -> Path:
    """Pull the audio track out of a media file and save it as MP3 next to it."""
    if not ffmpeg_available():
        raise MediaError("Audio extraction isn't available because FFmpeg isn't installed on the server.")
    target = source.with_name(safe_stem(source.name) + ".mp3")
    if target == source:
        return source
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(source), "-vn",
        "-codec:a", "libmp3lame", "-b:a", bitrate,
        str(target),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    except subprocess.TimeoutExpired:
        raise MediaError("Extracting the audio took too long. Try a shorter video.")
    except subprocess.CalledProcessError:
        raise MediaError("This file doesn't contain audio that can be extracted.")
    return target

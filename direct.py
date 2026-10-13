"""Direct media links: URLs that point straight at a video or audio file.

This is the most dependable path in Downloder, because it needs no platform
integration. Redirects are followed by hand so every hop is validated again.
"""
from pathlib import Path
from urllib.parse import unquote, urlparse

import httpx

from . import config
from .media import safe_stem
from .security import UnsafeURL, validate_url

MEDIA_EXTENSIONS = {
    ".mp4", ".m4v", ".mov", ".webm", ".mkv",
    ".mp3", ".m4a", ".aac", ".wav", ".ogg", ".flac",
}
GENERIC_TYPES = {"application/octet-stream", "binary/octet-stream", ""}


class NotMedia(Exception):
    pass


def _client() -> httpx.Client:
    return httpx.Client(
        follow_redirects=False,
        timeout=config.REQUEST_TIMEOUT,
        headers={"User-Agent": "Downloder/0.1"},
    )


def _open(client: httpx.Client, url: str) -> httpx.Response:
    """GET with streaming, following redirects only to validated public URLs."""
    for _ in range(config.MAX_REDIRECTS + 1):
        validate_url(url)
        try:
            response = client.send(client.build_request("GET", url), stream=True)
        except httpx.HTTPError:
            raise UnsafeURL("We couldn't reach that link. Check it and try again.")
        if response.is_redirect:
            location = response.headers.get("location")
            response.close()
            if not location:
                raise UnsafeURL("That link redirects somewhere we can't follow.")
            url = str(httpx.URL(url).join(location))
            continue
        return response
    raise UnsafeURL("That link redirects too many times.")


def _filename(url: str, response: httpx.Response) -> str:
    return unquote(Path(urlparse(str(response.url)).path).name) or "media"


def _is_media(response: httpx.Response, name: str) -> bool:
    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type.startswith(("video/", "audio/")):
        return True
    return content_type in GENERIC_TYPES and Path(name).suffix.lower() in MEDIA_EXTENSIONS


def probe(url: str) -> dict:
    """Describe a direct media link without downloading it. Raises NotMedia."""
    with _client() as client:
        response = _open(client, url)
        try:
            if response.status_code != 200:
                raise NotMedia
            name = _filename(url, response)
            if not _is_media(response, name):
                raise NotMedia
            size = response.headers.get("content-length")
            return {
                "title": safe_stem(name, "Media file"),
                "size_bytes": int(size) if size and size.isdigit() else None,
                "content_type": response.headers.get("content-type", ""),
            }
        finally:
            response.close()


def download(url: str, dest_dir: Path, on_progress) -> Path:
    """Save the original file. Calls on_progress(0..1) as bytes arrive."""
    with _client() as client:
        response = _open(client, url)
        try:
            if response.status_code != 200:
                raise UnsafeURL("The link didn't return a file. It may have expired or need a login.")
            name = _filename(url, response)
            if not _is_media(response, name):
                raise UnsafeURL("That link isn't a video or audio file.")

            total = response.headers.get("content-length")
            total = int(total) if total and total.isdigit() else None
            if total and total > config.MAX_FILE_BYTES:
                raise UnsafeURL("That file is larger than the server limit.")

            ext = Path(name).suffix.lower()
            if ext not in MEDIA_EXTENSIONS:
                ext = ".mp4" if response.headers.get("content-type", "").startswith("video/") else ".mp3"
            target = dest_dir / (safe_stem(name) + ext)

            received = 0
            with open(target, "wb") as handle:
                for chunk in response.iter_bytes(chunk_size=256 * 1024):
                    received += len(chunk)
                    if received > config.MAX_FILE_BYTES:
                        raise UnsafeURL("That file is larger than the server limit.")
                    handle.write(chunk)
                    if total:
                        on_progress(received / total)
            return target
        finally:
            response.close()

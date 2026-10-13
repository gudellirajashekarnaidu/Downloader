"""Ties the pieces together: analyze a link, then run a download job."""
import logging
import secrets
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from . import config, direct, extractors
from .media import MediaError, extract_mp3
from .security import UnsafeURL, match_platform, validate_url

log = logging.getLogger("downloder")

NOT_SUPPORTED = (
    "This link isn't supported yet. Paste a direct link to a video or audio file, "
    "or a public post from Instagram, X, or Telegram."
)


def analyze(raw_url: str) -> dict:
    url = validate_url(raw_url)
    platform = match_platform(url)

    if platform:
        info = extractors.analyze(url)
        return {"url": url, "platform": platform, "source": "page", **info}

    try:
        info = direct.probe(url)
    except direct.NotMedia:
        raise UnsafeURL(NOT_SUPPORTED)
    return {
        "url": url,
        "platform": "Direct link",
        "source": "direct",
        "title": info["title"],
        "thumbnail": None,
        "duration": None,
        "uploader": None,
        "size_bytes": info["size_bytes"],
        "qualities": [],
        "can_video": True,
        "can_audio": True,
    }


@dataclass
class Job:
    url: str
    kind: str
    quality: str | None
    id: str = field(default_factory=lambda: secrets.token_urlsafe(16))
    status: str = "queued"  # queued, working, done, failed
    progress: float = 0.0
    error: str | None = None
    file_path: Path | None = None
    filename: str | None = None
    created_at: float = field(default_factory=time.time)

    def public(self) -> dict:
        return {
            "id": self.id,
            "status": self.status,
            "progress": round(self.progress, 3),
            "kind": self.kind,
            "filename": self.filename,
            "error": self.error,
            "download_url": f"/api/jobs/{self.id}/file" if self.status == "done" else None,
        }


class JobStore:
    """Version A keeps jobs in memory. Version C swaps this for Redis + Celery."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="downloder")

    def create(self, raw_url: str, kind: str, quality: str | None) -> Job:
        url = validate_url(raw_url)
        job = Job(url=url, kind=kind, quality=quality)
        with self._lock:
            self._jobs[job.id] = job
        self._pool.submit(self._run, job)
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def sweep(self) -> None:
        """Delete expired jobs and their files."""
        cutoff = time.time() - config.FILE_TTL_SECONDS
        with self._lock:
            expired = [j for j in self._jobs.values() if j.created_at < cutoff and j.status in ("done", "failed")]
            for job in expired:
                del self._jobs[job.id]
        for job in expired:
            shutil.rmtree(config.WORK_DIR / job.id, ignore_errors=True)

    def _run(self, job: Job) -> None:
        job.status = "working"
        dest = config.WORK_DIR / job.id
        dest.mkdir(parents=True, exist_ok=True)

        def progress(value: float) -> None:
            job.progress = max(job.progress, min(value, 0.99))

        try:
            if match_platform(job.url):
                path = extractors.download(job.url, job.kind, job.quality, dest, progress)
            else:
                path = direct.download(job.url, dest, lambda v: progress(v * 0.9))
                if job.kind == "audio":
                    progress(0.92)
                    path = extract_mp3(path)
            job.file_path = path
            job.filename = path.name
            job.progress = 1.0
            job.status = "done"
        except (UnsafeURL, extractors.Unsupported, MediaError) as exc:
            self._fail(job, str(exc), dest)
        except Exception:
            log.exception("Job %s failed", job.id)
            self._fail(job, "Something went wrong while processing this media. Try again in a moment.", dest)

    @staticmethod
    def _fail(job: Job, message: str, dest: Path) -> None:
        job.error = message
        job.status = "failed"
        shutil.rmtree(dest, ignore_errors=True)


store = JobStore()

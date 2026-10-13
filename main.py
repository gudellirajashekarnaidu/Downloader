"""Downloder API. Run with: uvicorn app.main:app --reload"""
import asyncio
import shutil
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import config, extractors, service
from .media import ffmpeg_available
from .security import UnsafeURL


async def _sweeper() -> None:
    while True:
        await asyncio.sleep(60)
        service.store.sweep()


@asynccontextmanager
async def lifespan(_: FastAPI):
    shutil.rmtree(config.WORK_DIR, ignore_errors=True)  # start clean
    config.WORK_DIR.mkdir(parents=True, exist_ok=True)
    task = asyncio.create_task(_sweeper())
    yield
    task.cancel()


app = FastAPI(title="Downloder", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Simple per-IP limiter. Fine for one server; use Redis when you scale out.
_hits: dict[str, deque] = defaultdict(deque)


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = _hits[ip]
    while window and window[0] < now - 60:
        window.popleft()
    if len(window) >= config.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(429, "Too many requests. Wait a minute and try again.")
    window.append(now)


class AnalyzeRequest(BaseModel):
    url: str = Field(max_length=2048)


class JobRequest(BaseModel):
    url: str = Field(max_length=2048)
    kind: Literal["video", "audio"]
    quality: str | None = Field(default=None, pattern=r"^(best|\d{3,4})$")


@app.get("/api/health")
def health():
    return {"ok": True, "ffmpeg": ffmpeg_available()}


@app.post("/api/analyze")
def analyze(body: AnalyzeRequest, request: Request):
    rate_limit(request)
    try:
        return service.analyze(body.url)
    except (UnsafeURL, extractors.Unsupported) as exc:
        raise HTTPException(400, str(exc))


@app.post("/api/jobs", status_code=202)
def create_job(body: JobRequest, request: Request):
    rate_limit(request)
    try:
        job = service.store.create(body.url, body.kind, body.quality)
    except UnsafeURL as exc:
        raise HTTPException(400, str(exc))
    return job.public()


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    job = service.store.get(job_id)
    if job is None:
        raise HTTPException(404, "This download has expired. Analyze the link again.")
    return job.public()


@app.get("/api/jobs/{job_id}/file")
def job_file(job_id: str):
    job = service.store.get(job_id)
    if job is None or job.status != "done" or job.file_path is None or not job.file_path.exists():
        raise HTTPException(404, "This file isn't available. It may have expired.")
    return FileResponse(job.file_path, filename=job.filename)

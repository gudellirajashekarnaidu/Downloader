"""Settings for Downloder. Override with environment variables."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Where processed files live until they expire. This folder is emptied every time the
# server starts, so point it at a dedicated folder and nothing else.
WORK_DIR = Path(os.getenv("DOWNLODER_WORK_DIR", BASE_DIR / "work"))
FILE_TTL_SECONDS = int(os.getenv("DOWNLODER_FILE_TTL", "1800"))  # 30 minutes
MAX_FILE_BYTES = int(os.getenv("DOWNLODER_MAX_FILE_MB", "500")) * 1024 * 1024

# Network behaviour for direct links.
REQUEST_TIMEOUT = 15
MAX_REDIRECTS = 5
ALLOWED_PORTS = {80, 443}

# Abuse protection: requests per minute per IP (analyze + create job).
RATE_LIMIT_PER_MINUTE = int(os.getenv("DOWNLODER_RATE_LIMIT", "20"))

# Browser origins allowed to call the API (the Vite dev server by default).
ALLOWED_ORIGINS = os.getenv("DOWNLODER_CORS", "http://localhost:5173").split(",")

# Page links (posts, reels) are handled by the extractor engine, and ONLY for
# these hosts. Keeping this list short is also an SSRF defence: the extractor
# is never pointed at arbitrary user-supplied sites.
# YouTube is intentionally absent: its terms don't allow downloads outside
# YouTube's own features. Add hosts here only after checking the platform's terms.
EXTRACTOR_PLATFORMS = {
    "instagram.com": "Instagram",
    "x.com": "X",
    "twitter.com": "X",
    "t.me": "Telegram",
}

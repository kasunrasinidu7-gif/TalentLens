from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # The app can still run with process-level environment variables.
    def load_dotenv(*args, **kwargs):
        return False

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "data/scoutai.db"))
if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = ROOT / DATABASE_PATH
API_BASE_URL = os.getenv("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io").rstrip("/")
API_KEY = os.getenv("API_FOOTBALL_KEY", "").strip()
LEAGUES = [int(x) for x in os.getenv("API_FOOTBALL_LEAGUES", "39,40,41,42").split(",") if x.strip()]
SEASON = int(os.getenv("API_FOOTBALL_SEASON", "2025"))
SYNC_HOUR = int(os.getenv("SYNC_HOUR", "3"))

import sys
import time
from pathlib import Path
import schedule
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import SYNC_HOUR
from src.db import init_db
from src.pipeline import sync
from src.seed import seed_if_empty

init_db(); seed_if_empty(); print(sync())
schedule.every().day.at(f"{SYNC_HOUR:02d}:00").do(sync)
print(f"Daily sync scheduled for {SYNC_HOUR:02d}:00")
while True:
    schedule.run_pending(); time.sleep(30)

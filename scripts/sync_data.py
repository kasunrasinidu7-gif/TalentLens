from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.db import init_db
from src.pipeline import sync
from src.seed import seed_if_empty

if __name__ == "__main__":
    init_db(); seed_if_empty(); result = sync()
    print(result)

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from .config import DATABASE_PATH


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY, name TEXT NOT NULL, age INTEGER,
                position TEXT, nationality TEXT, team TEXT, league TEXT, foot TEXT,
                speed REAL, crossing REAL, dribbling REAL, passing REAL,
                finishing REAL, defending REAL, physicality REAL,
                appearances REAL, minutes REAL, goals REAL, assists REAL,
                market_value REAL, potential REAL, source TEXT NOT NULL,
                last_updated TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL,
                snapshot_date TEXT NOT NULL, appearances REAL, minutes REAL,
                goals REAL, assists REAL, market_value REAL, potential REAL,
                source TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sync_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT NOT NULL,
                finished_at TEXT NOT NULL, status TEXT NOT NULL,
                records_seen INTEGER, records_written INTEGER, message TEXT
            );
            """
        )


def upsert(players: list[dict]) -> tuple[int, int]:
    stamp = now()
    statement = """
    INSERT INTO players (player_id,name,age,position,nationality,team,league,foot,
      speed,crossing,dribbling,passing,finishing,defending,physicality,
      appearances,minutes,goals,assists,market_value,potential,source,last_updated)
    VALUES (:player_id,:name,:age,:position,:nationality,:team,:league,:foot,
      :speed,:crossing,:dribbling,:passing,:finishing,:defending,:physicality,
      :appearances,:minutes,:goals,:assists,:market_value,:potential,:source,:last_updated)
    ON CONFLICT(player_id) DO UPDATE SET
      name=excluded.name,age=excluded.age,position=excluded.position,
      nationality=excluded.nationality,team=excluded.team,league=excluded.league,
      foot=excluded.foot,speed=excluded.speed,crossing=excluded.crossing,
      dribbling=excluded.dribbling,passing=excluded.passing,finishing=excluded.finishing,
      defending=excluded.defending,physicality=excluded.physicality,
      appearances=excluded.appearances,minutes=excluded.minutes,goals=excluded.goals,
      assists=excluded.assists,market_value=excluded.market_value,
      potential=excluded.potential,source=excluded.source,last_updated=excluded.last_updated
    """
    with connect() as db:
        for player in players:
            row = {**player, "last_updated": player.get("last_updated", stamp)}
            db.execute(statement, row)
            db.execute(
                "INSERT INTO snapshots (player_id,snapshot_date,appearances,minutes,goals,assists,market_value,potential,source) VALUES (?,?,?,?,?,?,?,?,?)",
                (row["player_id"], stamp, row.get("appearances", 0), row.get("minutes", 0), row.get("goals", 0), row.get("assists", 0), row.get("market_value", 0), row.get("potential", 0), row.get("source", "unknown")),
            )
    return len(players), len(players)


def list_players() -> list[dict]:
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM players ORDER BY name")]


def history(player_id: str) -> list[dict]:
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM snapshots WHERE player_id=? ORDER BY snapshot_date", (player_id,))]


def sync_log(status: str, seen: int, written: int, message: str, started: str) -> None:
    with connect() as db:
        db.execute("INSERT INTO sync_runs (started_at,finished_at,status,records_seen,records_written,message) VALUES (?,?,?,?,?,?)", (started, now(), status, seen, written, message))


def latest_sync() -> dict | None:
    with connect() as db:
        row = db.execute("SELECT * FROM sync_runs ORDER BY id DESC LIMIT 1").fetchone()
    return dict(row) if row else None

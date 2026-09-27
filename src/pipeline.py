from __future__ import annotations

try:
    import requests
except ImportError:  # Only required when an external API key is configured.
    requests = None

from .config import API_BASE_URL, API_KEY, LEAGUES, SEASON
from .db import now, sync_log, upsert


def number(value, default=0) -> float:
    try:
        return float(default if value is None else value)
    except (TypeError, ValueError):
        return float(default)


def position_name(value: str | None) -> str:
    return {
        "attacker": "ATT",
        "midfielder": "MID",
        "defender": "DEF",
        "goalkeeper": "GK",
    }.get((value or "").lower(), (value or "").upper()[:3] or "UNK")


def normalize(item: dict, league_id: int) -> dict:
    player = item.get("player", {})
    stats = (item.get("statistics") or [{}])[0]
    games, goals, passes, dribbles, tackles = (stats.get(key) or {} for key in ("games", "goals", "passes", "dribbles", "tackles"))
    age = int(player.get("age") or 23)
    appearances = number(games.get("appearences"))
    minutes = number(games.get("minutes"))
    potential = min(99, max(45, 72 + (23 - age) * 2 + min(8, minutes / max(1, appearances * 90) * 8)))
    league = stats.get("league") or {}
    return {
        "player_id": f"api-football-{player.get('id')}", "name": player.get("name") or "Unknown",
        "age": age, "position": position_name(games.get("position")), "nationality": player.get("nationality") or "Unknown",
        "team": (stats.get("team") or {}).get("name") or "Unknown", "league": league.get("name") or f"League {league_id}", "foot": player.get("foot") or "Unknown",
        "speed": 0, "crossing": 0, "dribbling": min(99, number(dribbles.get("success")) * 1.1),
        "passing": number(passes.get("accuracy")), "finishing": min(99, number(goals.get("total")) / max(1, number(goals.get("total")) + 1) * 100),
        "defending": min(99, number(tackles.get("total")) * 2), "physicality": 0, "appearances": appearances, "minutes": minutes,
        "goals": number(goals.get("total")), "assists": number(goals.get("assists")), "market_value": 0, "potential": potential,
        "source": "api-football", "last_updated": now(),
    }


def fetch(league_id: int) -> list[dict]:
    if not API_KEY:
        raise RuntimeError("API_FOOTBALL_KEY is not configured")
    if requests is None:
        raise RuntimeError("Install requirements.txt before using the external API connector")
    response = requests.get(f"{API_BASE_URL}/players", headers={"x-apisports-key": API_KEY}, params={"league": league_id, "season": SEASON, "page": 1}, timeout=30)
    response.raise_for_status()
    return [normalize(item, league_id) for item in response.json().get("response", [])]


def sync() -> dict:
    started = now()
    if not API_KEY:
        message = "Skipped: no API_FOOTBALL_KEY configured; demo data remains available."
        sync_log("skipped", 0, 0, message, started)
        return {"status":"skipped", "seen":0, "written":0, "message":message}
    records, errors = [], []
    for league in LEAGUES:
        try: records.extend(fetch(league))
        except Exception as exc: errors.append(f"league {league}: {exc}")
    seen, written = upsert(records)
    status = "success" if not errors else "partial"
    message = "Configured leagues synced." if not errors else "Some leagues failed: " + "; ".join(errors)
    sync_log(status, seen, written, message, started)
    return {"status":status, "seen":seen, "written":written, "message":message}

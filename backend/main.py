from __future__ import annotations

import logging
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.config import API_KEY, LEAGUES
from src.pipeline import fetch
from src.scout import rank
from src.seed import SEED
from src.ml_model import MODEL_VERSION, PlayerMatcher

logger = logging.getLogger(__name__)

app = FastAPI(title="TalentLens MVP API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8765", "http://localhost:8765", "http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def load_players() -> tuple[dict, ...]:
    """Load current players for the request process without creating a database."""
    if not API_KEY:
        return tuple(SEED)

    players: list[dict] = []
    for league_id in LEAGUES:
        try:
            players.extend(fetch(league_id))
        except Exception as exc:  # one unavailable league must not break all search
            logger.warning("Unable to load league %s: %s", league_id, exc)
    return tuple(players or SEED)


def clear_runtime_cache() -> None:
    load_players.cache_clear()
    load_matcher.cache_clear()


@lru_cache(maxsize=1)
def load_matcher() -> PlayerMatcher:
    model = PlayerMatcher().fit(list(load_players()))
    try:
        model.save(__import__("pathlib").Path(__file__).resolve().parents[1] / "models" / "player_matcher.joblib")
    except Exception as exc:
        logger.warning("Unable to save model artifact: %s", exc)
    return model


def public_player(player: dict, score: float | None = None, reasons: list[str] | None = None) -> dict:
    return {
        "player_id": player["player_id"],
        "name": player["name"],
        "age": player.get("age"),
        "position": player.get("position"),
        "nationality": player.get("nationality"),
        "team": player.get("team"),
        "league": player.get("league"),
        "foot": player.get("foot"),
        "speed": round(float(player.get("speed") or 0)),
        "crossing": round(float(player.get("crossing") or 0)),
        "dribbling": round(float(player.get("dribbling") or 0)),
        "passing": round(float(player.get("passing") or 0)),
        "finishing": round(float(player.get("finishing") or 0)),
        "defending": round(float(player.get("defending") or 0)),
        "physicality": round(float(player.get("physicality") or 0)),
        "appearances": player.get("appearances", 0),
        "minutes": player.get("minutes", 0),
        "goals": player.get("goals", 0),
        "assists": player.get("assists", 0),
        "market_value": player.get("market_value", 0),
        "potential": round(float(player.get("potential") or 0)),
        "source": player.get("source", "unknown"),
        "last_updated": player.get("last_updated"),
        "match_score": score,
        "rule_score": player.get("rule_score"),
        "model_score": player.get("model_score"),
        "reasons": reasons or [],
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "data_mode": "api" if API_KEY else "demo", "players_loaded": len(load_players()), "model": load_matcher().metadata()}


@app.get("/api/search")
def search_players(
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    page_size: int = Query(8, ge=1, le=50),
    limit: int | None = Query(None, ge=1, le=1000),
) -> dict:
    """Rank the full in-memory dataset, then return one deterministic page."""
    requested_size = limit or page_size
    model = load_matcher()
    _, ranked = rank(list(load_players()), q, limit=1000, model_scores=model.score(q))
    total = len(ranked)
    start = (page - 1) * requested_size
    results = ranked[start:start + requested_size]
    return {
        "query": q,
        "data_mode": "api" if API_KEY else "demo",
        "model": model.metadata(),
        "page": page,
        "page_size": requested_size,
        "total": total,
        "has_next": start + requested_size < total,
        "count": len(results),
        "players": [public_player(row, row["match_score"], row["reasons"]) for row in results],
    }


@app.get("/api/model/status")
def model_status() -> dict:
    return load_matcher().metadata()


@app.post("/api/model/train")
def train_model() -> dict:
    clear_runtime_cache()
    model = load_matcher()
    return {"status": "trained", **model.metadata()}


@app.get("/api/players/{player_id}")
def player_details(player_id: str) -> dict:
    player = next((row for row in load_players() if row["player_id"] == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found in the current data source")

    strengths = []
    for field, label in (("speed", "Speed"), ("crossing", "Crossing"), ("dribbling", "Dribbling"), ("passing", "Passing")):
        if float(player.get(field) or 0) >= 80:
            strengths.append({"label": label, "value": round(float(player[field]))})
    improvements = []
    for field, label in (("defending", "Defending"), ("finishing", "Finishing"), ("physicality", "Physicality")):
        if float(player.get(field) or 0) < 60:
            improvements.append(f"Develop {label.lower()} consistency")
    if not improvements:
        improvements.append("Continue development against stronger opposition")

    return {
        **public_player(player),
        "strengths": strengths,
        "areas_for_improvement": improvements,
        "league_readiness": min(99, round(float(player.get("potential") or 0) * 0.9)),
        "value_history": [],
        "message": "Live player details returned from the configured data source." if API_KEY else "Demo player details returned. Add an API key for live data.",
    }


@app.post("/api/cache/refresh")
def refresh_cache() -> dict:
    clear_runtime_cache()
    return {"status": "refreshed", "players_loaded": len(load_players())}

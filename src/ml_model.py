"""Content-based player matching model for the TalentLens MVP.

This is a real trainable recommender, not a claim about future market value:
it fits a TF-IDF representation on the current player corpus and compares a
natural-language scouting request with each player's available profile text.
The transparent football constraints in scout.py remain part of the hybrid
score so a user can still see why a player ranked highly.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .scout import parse


MODEL_VERSION = "tfidf-hybrid-matcher-v1"


POSITION_TERMS = {
    "ATT": "attacker forward striker winger wide",
    "MID": "midfielder central midfielder box to box",
    "DEF": "defender centre back center back full back",
    "GK": "goalkeeper keeper",
}


class PlayerMatcher:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = None
        self.player_ids: list[str] = []
        self.training_samples = 0
        self.trained_at: str | None = None

    @staticmethod
    def player_document(player: dict) -> str:
        position = player.get("position") or "unknown"
        age = int(player.get("age") or 0)
        age_terms = "young u21" if age <= 21 else "young" if age <= 23 else ""
        return " ".join(
            str(value)
            for value in (
                player.get("name"),
                position,
                POSITION_TERMS.get(position, ""),
                player.get("team"),
                player.get("league"),
                player.get("nationality"),
                player.get("foot"),
                age_terms,
            )
            if value
        )

    @staticmethod
    def query_document(query: str) -> str:
        request = parse(query)
        extra = [query]
        if request.position:
            extra.append(POSITION_TERMS.get(request.position, request.position))
        if request.max_age:
            extra.append("young u21" if request.max_age <= 21 else "young")
        if request.speed is not None:
            extra.append("speed pace acceleration")
        if request.crossing is not None:
            extra.append("crossing delivery wide service")
        if request.potential is not None:
            extra.append("potential development")
        if request.resale:
            extra.append("resale upside value development")
        return " ".join(extra)

    def fit(self, players: list[dict]) -> "PlayerMatcher":
        self.player_ids = [str(player["player_id"]) for player in players]
        documents = [self.player_document(player) for player in players]
        self.matrix = self.vectorizer.fit_transform(documents)
        self.training_samples = len(players)
        self.trained_at = datetime.now(timezone.utc).isoformat()
        return self

    def score(self, query: str) -> dict[str, float]:
        if self.matrix is None:
            return {}
        query_vector = self.vectorizer.transform([self.query_document(query)])
        values = cosine_similarity(query_vector, self.matrix)[0]
        return {player_id: round(float(value * 100), 1) for player_id, value in zip(self.player_ids, values)}

    def metadata(self) -> dict:
        return {
            "version": MODEL_VERSION,
            "type": "content-based TF-IDF hybrid recommender",
            "trained": self.matrix is not None,
            "training_samples": self.training_samples,
            "features": "player name, role, club, league, nationality, foot, age profile",
            "trained_at": self.trained_at,
        }

    def save(self, path: Path) -> None:
        import joblib

        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

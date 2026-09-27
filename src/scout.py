from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Request:
    position: str | None = None
    max_age: int | None = None
    speed: float | None = None
    crossing: float | None = None
    potential: float | None = None
    resale: bool = False


POSITIONS = {"right winger":"RW","right wing":"RW","rw":"RW","left winger":"LW","left wing":"LW","lw":"LW","striker":"ST","forward":"ST","st":"ST","central midfielder":"CM","cm":"CM","centre back":"CB","center back":"CB","cb":"CB","goalkeeper":"GK","keeper":"GK","gk":"GK"}


def parse(text: str) -> Request:
    value = text.lower()
    request = Request()
    for phrase, position in sorted(POSITIONS.items(), key=lambda item: len(item[0]), reverse=True):
        if phrase in value:
            request.position = position
            break
    age = re.search(r"(?:under|below|younger than|max(?:imum)?)\s+(\d{2})", value)
    if age:
        request.max_age = int(age.group(1))
    elif "u21" in value or "under-21" in value:
        request.max_age = 21
    elif "young" in value:
        request.max_age = 23
    request.speed = 86 if "excellent speed" in value or "very good speed" in value else 78 if "good speed" in value else 70 if "speed" in value else None
    request.crossing = 82 if "excellent crossing" in value or "very good crossing" in value else 72 if "good crossing" in value else 64 if "decent crossing" in value else None
    request.potential = 86 if "high potential" in value or "excellent potential" in value else 78 if "potential" in value else None
    request.resale = any(word in value for word in ("resale", "sell", "profit", "affordable", "value"))
    return request


def rank(players: list[dict], text: str, limit: int = 5, model_scores: dict[str, float] | None = None) -> tuple[Request, list[dict]]:
    request = parse(text)
    output = []
    for player in players:
        score, reasons = 0.0, []
        if request.position:
            actual_position = player.get("position")
            if actual_position == request.position:
                score += 30; reasons.append(f"matches {request.position}")
            elif request.position in ("RW", "LW", "ST") and actual_position in ("ATT", "ST", "FWD"):
                score += 12; reasons.append("listed as an attacker; exact wide role needs verification")
            elif request.position == "CM" and actual_position in ("MID", "CM"):
                score += 12; reasons.append("listed as a midfielder; exact role needs verification")
            else:
                score -= 25
        if request.max_age:
            if player["age"] <= request.max_age:
                score += 12; reasons.append(f"is {player['age']} years old")
            else:
                score -= min(12, (player["age"] - request.max_age) * 2)
        for field, minimum, label, weight in (("speed",request.speed,"speed",.20),("crossing",request.crossing,"crossing",.18),("potential",request.potential,"potential",.25)):
            if minimum is not None:
                current = float(player.get(field) or 0)
                score += max(0, min(20, (current - minimum + 20) * weight))
                if current >= minimum: reasons.append(f"has {label} rated {current:.0f}")
        if request.resale:
            age = player.get("age") or 30
            value = player.get("market_value") or 0
            value_bonus = max(0, 12 - value / 500000) if value else 0
            score += min(18, value_bonus + max(0, 24 - age) / 3 + max(0, player.get("potential", 0) - 70) / 5)
            if age <= 23: reasons.append("young enough for resale upside")
            if value: reasons.append(f"estimated value £{value:,.0f}")
            else: reasons.append("market value unavailable from this data source")
        score += min(8, (player.get("appearances") or 0) / 5)
        rule_score = round(max(0, min(100, score)), 1)
        semantic_score = round(float((model_scores or {}).get(str(player["player_id"]), 0)), 1)
        if model_scores is not None:
            score = round(rule_score * 0.65 + semantic_score * 0.35, 1)
            if semantic_score >= 35:
                reasons.insert(0, f"AI profile similarity {semantic_score:.0f}%")
        output.append({**player, "match_score": round(max(0, min(100, score)), 1), "rule_score": rule_score, "model_score": semantic_score, "reasons": reasons})
    output.sort(key=lambda row: row["match_score"], reverse=True)
    return request, output[:limit]

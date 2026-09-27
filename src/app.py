from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.db import history, init_db, latest_sync, list_players
from src.pipeline import sync
from src.scout import rank
from src.seed import seed_if_empty

st.set_page_config(page_title="ScoutAI", page_icon="⚽", layout="wide")
init_db(); seed_if_empty()
st.title("⚽ ScoutAI")
st.caption("Natural-language football scouting with automatic data updates")
players = list_players(); latest = latest_sync()

with st.sidebar:
    st.header("Data pipeline")
    if latest:
        st.write(f"Last sync: {latest['finished_at']}")
        st.write(f"Status: {latest['status']}")
        st.write(f"Records written: {latest['records_written']}")
        st.caption(latest['message'])
    if st.button("Run data sync now", use_container_width=True):
        with st.spinner("Syncing configured leagues..."):
            result = sync()
        st.success(f"{result['status'].title()}: {result['written']} records written")
        st.rerun()

st.subheader("Describe the player you need")
text = st.text_area("Scouting request", "Find me a young right winger with good speed, decent crossing, high potential, and strong resale value.", height=100)
if st.button("Find players", type="primary"):
    request, results = rank(players, text)
    st.write({"position": request.position or "any", "max age": request.max_age or "any", "speed": request.speed or "any", "crossing": request.crossing or "any", "potential": request.potential or "any", "resale focus": request.resale})
    for player in results:
        with st.container(border=True):
            left, middle, right = st.columns([2, 3, 1])
            with left:
                st.markdown(f"### {player['name']}")
                st.write(f"{player['position']} · {player['age']} · {player['team']} · {player['league']}")
            with middle:
                st.write("**Why:** " + (", ".join(player['reasons']) or "general statistical fit"))
                st.caption(f"Source: {player['source']} · Updated: {player['last_updated']}")
            with right: st.metric("Match score", f"{player['match_score']:.0f}%")
            snapshots = history(player['player_id'])
            if len(snapshots) > 1:
                st.line_chart(pd.DataFrame(snapshots).set_index('snapshot_date')[['market_value', 'potential']])

st.divider(); st.subheader("Player database")
columns = ["name", "position", "age", "team", "league", "speed", "crossing", "potential", "market_value", "source", "last_updated"]
st.dataframe(pd.DataFrame(players)[columns], use_container_width=True, hide_index=True)

# TalentLens

TalentLens is a football scouting MVP that accepts natural-language requirements, ranks players, explains recommendations, and can fetch current player data on demand.

Example request:

> Find me a young right winger with good speed, decent crossing, Championship potential, and high resale value.

## Run the MVP

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

In another terminal, run the Next.js frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The frontend uses the Next.js App Router. Reusable UI components live in `frontend/components`, page routes live in `frontend/app`, and API requests are in `frontend/lib/api.ts`. Set `NEXT_PUBLIC_API_BASE_URL` only if the backend is not running at `http://127.0.0.1:8000`.

Copy `.env.example` to `.env` and add an API-Football key when you are ready for live data. Without a key, the API uses the demo players.

The MVP intentionally does not store user accounts, searches, saved players, or favorites. Player data is fetched and analyzed during a search. The old Stitch HTML prototype is preserved under `frontend/legacy-stitch/` for reference.

## Matching model

The current AI baseline is a content-based TF-IDF hybrid recommender. It trains on the connected player corpus, compares a natural-language request with each available player profile, and combines that similarity with transparent football constraints. It is not yet a supervised market-value or career-potential predictor because that requires labelled historical scouting outcomes.

The model trains automatically on the first search. To train it explicitly:

```powershell
py scripts/train_model.py
```

Model status is available at `GET /api/model/status`; retraining the live corpus is available at `POST /api/model/train`.

To sync manually:

```powershell
py scripts\sync_data.py
```

To run a daily sync process:

```powershell
py scripts\scheduler.py
```

Market value and potential are estimates, not guarantees. The API currently uses a transparent ranking engine and can later be upgraded to a trained ML model.

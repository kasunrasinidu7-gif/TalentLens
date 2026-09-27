# TalentLens temporary frontend

This folder contains the desktop UI generated from the Stitch package:

- `index.html` — natural-language scout search
- `results.html` — matched players
- `player.html` — player details
- `navigation.js` — temporary navigation between screens

The visual design is intentionally kept as the generated baseline for now. The Python scouting backend remains in `src/`; the frontend can be replaced later without changing the data model or ranking logic.

To preview locally with Python:

```powershell
python -m http.server 8000 --directory frontend
```

Then open `http://localhost:8000`.

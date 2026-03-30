# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

To run the Rock Paper Scissors game:

```bash
python3 server.py
```

Then open http://localhost:8765 in a browser.

## Project Overview

A lightweight Rock Paper Scissors web game with a persistent all-time leaderboard. No build step, no external dependencies, no testing framework.

## Architecture

**Backend (server.py)**
- Single Python HTTP server using `http.server.BaseHTTPRequestHandler`
- Three endpoints:
  - `GET /` → serves rock-paper-scissors.html
  - `GET /leaderboard` → returns players sorted by wins desc, then win_rate desc
  - `POST /score` → records a game result (win/loss/draw) for a player
- CORS enabled for all origins
- Silences request logging to keep output clean

**Frontend (rock-paper-scissors.html)**
- Single HTML file with embedded CSS and JavaScript (no build step)
- Name modal for player setup (localStorage not used, so names are session-only on frontend but persistent in server leaderboard)
- Game arena displays both player and CPU choices with emoji
- Session scoreboard tracks current session stats (reset with "Reset Session" button)
- All-time leaderboard fetched via `GET /leaderboard` after each game
- Graceful fallback: if server unavailable, shows message to start server

**Data (scores.json)**
- JSON file with flat structure: `{ "playerName": { "wins": N, "losses": N, "draws": N }, ... }`
- Auto-created on first score submission
- Sorted alphabetically by player name when loaded

## Key Implementation Details

### Game Logic (frontend)
- CPU randomly picks rock/paper/scissors using `options[Math.floor(Math.random() * 3)]`
- Win conditions defined in `wins` object: rock beats scissors, scissors beats paper, paper beats rock
- Shake animation on emoji display for visual feedback

### Leaderboard Ranking (backend)
- Two-level sort: primary by wins (descending), secondary by win_rate (descending)
- Win rate calculated as `wins / (wins + losses + draws) * 100`, rounded to 1 decimal
- Returns all players, not paginated
- Medals shown for top 3; others numbered by rank

### Player Tracking
- Player name submitted in name modal at start
- Frontend sends name with every score POST
- No user accounts or authentication; leaderboard is completely public
- Same player name can be entered by anyone to add to their stats

### API Contract
POST `/score` body:
```json
{ "name": "string (required, max appears to be 24 chars)", "result": "win|loss|draw" }
```

Response on success:
```json
{ "ok": true, "stats": { "wins": N, "losses": N, "draws": N } }
```

Response on invalid payload (missing name, invalid result):
```json
{ "error": "Invalid payload" }
```

## File Structure

- `server.py` — HTTP server, leaderboard API, score persistence
- `rock-paper-scissors.html` — complete frontend (CSS + JS included)
- `scores.json` — leaderboard data (auto-created)
- `.gitignore` — ignores scores.json and Python cache

## Git & Github Workflow

All work is committed to Git and pushed to Github for version control and easy reversion.

**Commit practices:**
- Write clean, descriptive commit messages focusing on the "why"
- Create new commits for each logical unit of work
- Push to Github after completing work
- See memory for details on this workflow

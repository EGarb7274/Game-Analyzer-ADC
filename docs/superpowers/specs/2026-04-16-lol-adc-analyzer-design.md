# League of Legends ADC Analyzer — Design Spec
**Date:** 2026-04-16  
**Status:** Approved

---

## Overview

A Windows desktop application that allows a League of Legends player to analyze their own ADC match history and performance. The app provides post-game analysis only (no live overlay). Built with Python and PyQt6.

---

## Architecture

The app is structured in three layers:

### 1. Data Layer
- Uses the `riotwatcher` Python library as the Riot API client
- Resolves Riot ID (username + tag) to a PUUID on first lookup
- Fetches match IDs, match data, and match timelines from the Riot API
- All API responses are cached in a local SQLite database to avoid redundant fetches and enable offline access
- Champion, item, and rune metadata sourced from Riot's Data Dragon (bundled JSON, refreshable on demand)
- Build and rune recommendations sourced from a static community dataset (bundled JSON, updated manually or on app launch)

### 2. Analysis Layer
- Processes raw match data into derived statistics:
  - KDA (Kills / Deaths / Assists)
  - CS/min (creep score per minute)
  - Damage share (player damage as % of team total)
  - Gold earned
  - Vision score
  - Kill participation (%)
  - Item purchase timings (from match timeline events)
  - Positioning events (kill/death/assist coordinates from timeline, rendered as minimap heatmap)
- Surfaces recommended builds, rune pages, and skill orders per champion from bundled dataset

### 3. UI Layer
- Built with PyQt6
- Sidebar navigation between four main views
- Charts via matplotlib embedded in PyQt6 widgets

---

## Features

### Summoner Dashboard
- User enters Riot ID (username + tag) on first launch
- Displays summary across last N matches (configurable, default 20):
  - Overall win rate
  - Average KDA
  - Most played ADC champions
  - Average CS/min

### Match History View
- Scrollable table of recent matches
- Columns: Champion, Win/Loss, KDA, CS/min, Damage Dealt, Game Duration, Items Purchased
- Click any row to open Match Detail View

### Match Detail View
Deep dive into a single game, with three panels:

**Stats Panel:**
- KDA, CS/min, damage share, gold earned, vision score, kill participation

**Item Timing Chart:**
- Timeline visualization showing when each item was purchased (in minutes)

**Positioning Heatmap:**
- Minimap overlay showing locations of kills, deaths, and assists (sourced from Riot timeline event coordinates)
- Note: The Riot public API provides position data at discrete events only (not continuous frame tracking). This heatmap approximates positioning tendencies rather than showing full movement paths.

**Runes Used:**
- Display of the actual rune page taken in that match

### Builds & Runes Reference Panel
- Per-champion view for ADC champions
- Shows: recommended build path, rune page, skill order
- Data sourced from bundled community dataset (Data Dragon + static build reference)

---

## Data Flow

1. User enters Riot ID → API resolves to PUUID
2. App fetches last N match IDs for PUUID → checks SQLite cache for each
3. Uncached matches are fetched (match data + timeline) and stored in SQLite
4. Analysis layer processes stored data → UI renders results
5. Build/rune data loaded from bundled JSON; refreshable on demand

**Caching strategy:** Match data is immutable post-game. Cached matches are never re-fetched. Only the match ID list is re-fetched on refresh to discover new games.

---

## API Key Handling

- User provides their own Riot API key (free from developer.riotgames.com)
- Key entered via a settings screen on first launch
- Stored locally in a config file (plaintext, local only)
- Invalid/expired key → redirect to settings screen with setup instructions

---

## Error Handling

| Scenario | Behavior |
|---|---|
| Riot API rate limit hit | Automatic retry with exponential backoff; progress shown in UI |
| Invalid Riot ID | Clear error message prompting correction |
| Network unavailable | Load from SQLite cache where possible; show offline banner |
| Missing/expired API key | Redirect to settings screen with instructions |

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| UI Framework | PyQt6 |
| Charts | matplotlib (embedded in PyQt6) |
| Riot API Client | riotwatcher |
| Local Database | SQLite (via Python's built-in `sqlite3`) |
| Game Data | Riot Data Dragon (bundled JSON) |

---

## Out of Scope

- Real-time / in-game overlay
- Analysis of roles other than ADC
- Multiplayer or shared accounts
- Web or mobile interface

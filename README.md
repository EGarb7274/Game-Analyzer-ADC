# Game Analyzer ADC

Project repository for the Game Analyzer ADC.

---

## Task Log

### 2026-04-16 10:51 UTC - Create project skill and initialize repository
**What:** Created a local `task-documentation` skill that logs completed tasks to this README via the GitHub API. Created this GitHub repository and pushed an initial README.
**Why:** User requested a persistent audit trail of work done on this project, tracked directly in the repo.

### 2026-04-19 09:08 UTC - Task 1: Project Setup
**What:** Created the full project scaffold for the LoL ADC Analyzer — directory structure (`src/api`, `src/db`, `src/analysis`, `src/ui/views`, `tests`, `data`), all `__init__.py` files, `requirements.txt`, `.gitignore`, stub `main.py`, installed all dependencies (PyQt6, matplotlib, riotwatcher, requests, pytest), initialized the git repo, and made the first commit.
**Why:** Establishes the foundational file structure and dependency set required before any feature code can be written.

### 2026-04-19 09:32 UTC - Task 2: Config Module
**What:** Created `config.py` with `load_config` and `save_config` functions backed by `~/.lol_adc_analyzer/config.json`, with defaults for api_key, region, match_region, and match_count. Created `tests/test_config.py` with 3 passing tests covering defaults, save/load roundtrip, and missing-key merging.
**Why:** The app needs persistent config (API key + region) to make Riot API calls; this module provides that foundation with TDD-verified correctness.

### 2026-04-19 09:35 UTC - Task 3: SQLite Schema and Cache
**What:** Created `src/db/schema.py` with `init_db` (4 tables: summoners, match_ids, matches, match_timelines) and `open_db`. Created `src/db/cache.py` with full read/write functions for all tables. Fixed a `row_factory` bug by setting `sqlite3.Row` inside `init_db` so any connection gets named-column access. All 8 tests pass.
**Why:** The app needs a local SQLite cache to avoid re-fetching match data from the Riot API on every launch; this layer persists summoner, match, and timeline data between sessions.

### 2026-04-19 09:39 UTC - Task 4: Riot API Client
**What:** Created `src/api/riot_client.py` with `RiotClient` wrapping riotwatcher — `get_puuid`, `get_match_ids`, `get_match`, `get_timeline`, all backed by `_call_with_retry` for 429 rate-limit handling. Created `tests/test_riot_client.py` with 5 passing tests covering each method and retry logic. Fixed a test bug: `riotwatcher.ApiError` is `requests.HTTPError` and requires `response=` as a keyword arg, not positional.
**Why:** All match data fetching flows through the Riot API; the retry wrapper ensures the app handles rate limits gracefully without crashing.

### 2026-04-19 09:42 UTC - Task 5: Data Dragon Loader
**What:** Created `src/api/data_dragon.py` with a `DataDragon` class that lazily fetches and locally caches item data, champion data, and the minimap image from Riot's Data Dragon CDN. Created `data/builds.json` with bundled build/rune/skill-order recommendations for 5 ADC champions (Jinx, Jhin, Caitlyn, Ezreal, Kai'Sa). Import verified clean.
**Why:** The UI needs item names, champion names, and a minimap background without making live API calls on every render; Data Dragon provides this static game data with a local cache to avoid repeated network requests.

### 2026-04-19 09:45 UTC - Task 6: Stats Analysis
**What:** Created `src/analysis/stats.py` with `get_participant`, `calc_kda`, `calc_cs_per_min`, `calc_damage_share`, `calc_kill_participation`, and `extract_match_stats`. All 7 tests pass including kill participation returning values over 100% (correct LoL behaviour when kills+assists exceed team kills).
**Why:** The dashboard and match detail views need derived per-game statistics (KDA, CS/min, damage share, kill participation) computed from raw Riot API match JSON.

### 2026-04-19 09:48 UTC - Task 7: Timeline Analysis
**What:** Created `src/analysis/timeline.py` with `get_participant_id` (maps PUUID to 1-based participantId), `extract_item_timings` (returns item purchases with timestamps in minutes), and `extract_position_events` (returns kill/death/assist map coordinates from CHAMPION_KILL events). All 7 tests pass.
**Why:** The match detail view needs item purchase timelines for the timing chart and kill/death/assist positions for the heatmap — both derived from the raw timeline JSON the Riot API provides.

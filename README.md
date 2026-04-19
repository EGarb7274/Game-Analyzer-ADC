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

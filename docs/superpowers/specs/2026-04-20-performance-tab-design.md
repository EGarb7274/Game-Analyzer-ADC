# Performance Tab — Design Spec
**Date:** 2026-04-20  
**Status:** Approved

---

## Goal

Add a "Performance" view to the LoL ADC Analyzer that helps the user track improvement over time and identify specific weaknesses across a rolling window of recent matches.

---

## Navigation

A fourth sidebar item — **Performance** — is added to the existing nav (`Dashboard`, `Match History`, `Builds & Runes`). No other nav changes.

---

## Layout

The view is a vertically scrollable `QScrollArea` with two major sections:

1. **Trends** — line charts across the rolling window
2. **Weaknesses** — three diagnostic panels with auto-generated insights

A **rolling window selector** (button group: `Last 10` / `Last 20` / `Last 50`) sits at the top and controls all charts. Changing the selection re-renders every chart on the page. Defaults to Last 20.

---

## Section 1 — Trends

Five matplotlib line charts arranged in a 2-column grid. The 5th chart (Vision Score) spans both columns.

| Chart | Y-axis | Reference line (dashed) |
|-------|--------|------------------------|
| Win Rate | % | 50% |
| KDA | ratio | 3.0 |
| CS/min | float | 7.0 |
| Damage Share | % | 25% |
| Vision Score | int | 25 |

**Per chart:**
- X axis: match index (1 = oldest in window, N = most recent)
- Each point colored gold if above reference, muted red if below
- Thin dashed horizontal reference line
- Dark LoL theme (matching existing chart style: `#1a1a2e` background, `#c89b3c` accent)

**Data source:** `extract_match_stats()` on cached match data — no new API calls or analysis functions needed.

---

## Section 2 — Weaknesses

Three cards, each containing a matplotlib chart and a one-sentence auto-generated insight string displayed beneath it.

---

### 2a — Laning Phase

**Chart:** Dual-line chart — CS at 10 min and CS at 15 min across the rolling window. Second chart beneath it: gold differential at 10 and 15 min (positive = ahead, negative = behind, zero line shown).

**Insight logic:**
- If avg CS at 10 < 60: *"You average {n} CS at 10 min — most strong ADC players hit 70+."*
- If avg CS at 10 >= 70: *"Your 10-min CS average of {n} is solid."*
- If avg gold diff at 15 < -300: *"You're averaging {n} gold behind at 15 min — focus on surviving and farming safely."*

**New code required:** `extract_early_stats(timeline_data, participant_id) -> dict` in `src/analysis/timeline.py`. Returns `cs_at_10`, `cs_at_15`, `gold_diff_at_10`, `gold_diff_at_15` by scanning timeline frames at the 10:00 and 15:00 minute marks.

---

### 2b — Death Patterns

**Chart:** Horizontal bar histogram — death count bucketed into game-time bands: `0–10 min`, `10–20 min`, `20–30 min`, `30+ min`, aggregated across the rolling window.

**Insight logic:**
- Find the bucket with the most deaths
- `0–10`: *"Most deaths happen early — consider playing safer in laning phase."*
- `10–20`: *"Most deaths occur in mid-game transitions — watch your positioning when roaming."*
- `20–30`: *"Most deaths happen 20–30 min — a common sign of overextending after winning lane."*
- `30+`: *"Late-game deaths dominate — focus on positioning in teamfights and objectives."*

**Data source:** Timeline kill/death events already extracted by `extract_position_events()`. Death timestamp is available from `CHAMPION_KILL` events where the victim matches the participant.

---

### 2c — Vision Control

**Chart:** Three overlaid line charts across the rolling window: vision score, wards placed, control wards purchased.

**Insight logic:**
- If avg control wards < 1.5: *"You average {n:.1f} control wards per game — aim for 2+ as ADC."*
- If avg vision score < 20: *"Your vision score averages {n} — try placing wards more actively."*
- Otherwise: *"Your vision control is consistent — keep it up."*

**New data extraction:** `wardsPlaced` and `visionWardsBoughtInGame` from the participant stats block already stored in the match JSON cache. These are added to `extract_match_stats()` return dict.

---

## New Files

| File | Purpose |
|------|---------|
| `src/ui/views/performance.py` | New `PerformanceView` widget |

## Modified Files

| File | Change |
|------|--------|
| `src/ui/app.py` | Add `PerformanceView` to stack, add sidebar item |
| `src/analysis/stats.py` | Add `wards_placed`, `control_wards` to `extract_match_stats()` return |
| `src/analysis/timeline.py` | Add `extract_early_stats()` function |

---

## Data Flow

```
SQLite cache
    └── match JSON  →  extract_match_stats()  →  trend charts + vision panel
    └── timeline JSON  →  extract_early_stats()  →  laning panel
                       →  extract_position_events()  →  death pattern panel
```

No new API calls. All data is already cached locally.

---

## Error / Empty States

- If fewer matches exist than the selected window (e.g. only 8 matches, window = 20): use all available matches, show count in subtitle.
- If timeline data is missing for a match: skip that match for laning/death panels, note the gap.
- If no summoner is loaded: show a prompt directing the user to the Dashboard.

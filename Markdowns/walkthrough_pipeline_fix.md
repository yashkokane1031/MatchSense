# MatchSense — Season Derivation Root-Cause Fix Walkthrough

## Problem

`sync_pipeline.py` hardcoded `season_code="2526"` and `season_label="2025-26"` as function parameter defaults. This meant the weekly sync pipeline would never automatically cross a season boundary — every roster update (promotions, relegations) had to be manually patched into constants files, which is exactly how the incorrect "Coventry + Sunderland" hybrid roster landed in commit `f3ab129`.

The deeper issue: `ingestion.py`'s `DEFAULT_SEASONS` was also a static list ending at `2025-26`, so even `load_all_seasons()` would never include the current season's data without a code change.

---

## Fix: API-First Dynamic Season Derivation

### Architecture

```
                     ┌─────────────────────────────────────┐
                     │  Football-Data.org API               │
                     │  GET /competitions/PL/matches        │
                     │  → season.startDate / season.endDate │
                     └────────────────┬────────────────────┘
                                      │ (1) Primary: extract
                                      │     active season
                                      ▼
                   ┌───────────────────────────────────────┐
                   │  derive_current_season(api_season=...)│
                   │  ─────────────────────────────────────│
                   │  if api_season → use it (authoritative)│
                   │  else → date-math fallback            │
                   │    month ≥ 8 → year/(year+1)          │
                   │    month < 8 → (year-1)/year          │
                   └────────────────┬──────────────────────┘
                                    │ (season_code, season_label)
                          ┌─────────┴─────────┐
                          ▼                   ▼
              ┌──────────────────┐  ┌──────────────────────┐
              │ sync_pipeline.py │  │ ingestion.py          │
              │ Phase A ingestion│  │ derive_training_window│
              │ → CSV download   │  │ → 4-season sliding   │
              │ → fixture upsert │  │   window for training │
              └──────────────────┘  └──────────────────────┘
```

### Why API-First Matters

The date-math fallback has a known two-week blind spot every August: `month >= 8` reports the new season as active before the first ball is kicked. If a Tuesday cron runs during that window, the pipeline would attempt to ingest a season that doesn't exist yet in any data source — a plausible-looking wrong answer, not a crash. Making the API authoritative eliminates this.

### Key Files

#### [NEW] [`ml/data/season.py`](file:///d:/Yash Kokane/Projects/MatchSense/ml/data/season.py)

- `derive_current_season(api_season=None, now=None)` — API-first, date-math fallback
- `derive_season_from_date(now=None)` — pure date arithmetic (deterministic, testable)
- `derive_training_window(current_code, window_size=4)` — sliding window for training data

#### [MODIFY] [`scripts/sync_pipeline.py`](file:///d:/Yash Kokane/Projects/MatchSense/scripts/sync_pipeline.py)

- `run_phase_a_ingestion()` now probes Football-Data.org first (before any DB writes), extracts the API's reported season, then passes it to `derive_current_season(api_season=...)`.
- If the API is unreachable, `api_season` is `None` and the date-math fallback activates.
- Explicit `season_code`/`season_label` parameters still work for manual overrides (e.g. backfilling historical seasons).

#### [MODIFY] [`ml/data/ingestion.py`](file:///d:/Yash Kokane/Projects/MatchSense/ml/data/ingestion.py)

- Added `default_training_seasons()` function that computes the 4-season sliding window dynamically.
- `load_all_seasons(seasons=None)` now calls `default_training_seasons()` instead of reading the static `DEFAULT_SEASONS` constant.
- The old `DEFAULT_SEASONS` constant is kept but marked deprecated for backward compatibility.

---

## Commit History

```
e10050a fix(data): correct 2026-27 promoted/relegated roster (supersedes f3ab129)
b94aa93 fix(pipeline): derive season dynamically from Football-Data.org API with date-math fallback
f3ab129 feat: add Coventry City and Sunderland promoted team support to backend and frontend  ← wrong roster
```

The ordering is intentional: the root-cause fix (`b94aa93`) lands first, then the roster correction (`e10050a`) is clearly the *last manual patch* — making it obvious to any future reader that this class of manual intervention should never be needed again.

---

## Test Results

### Season Derivation Unit Tests (19/19)

| Test Class | Tests | Status |
|---|---|---|
| `TestSeasonConversions` | 3 | ✅ |
| `TestDeriveSeasonFromDate` | 6 | ✅ |
| `TestDeriveCurrentSeason` | 6 (incl. early-August edge cases) | ✅ |
| `TestDeriveTrainingWindow` | 4 | ✅ |

### Full Backend (130/130)

All unit + integration tests pass, including:
- 6 sync pipeline integration tests (2 new: API-derived season + API-down fallback)
- 19 season derivation unit tests (new)
- 105 existing tests (no regression)

### Frontend (18/18)

All Vitest unit + integration tests pass unchanged.

### Dry-Run Verification

```
Current season: ('2627', '2026-27')
Training window:
  {'code': '2324', 'label': '2023-24'}
  {'code': '2425', 'label': '2024-25'}
  {'code': '2526', 'label': '2025-26'}
  {'code': '2627', 'label': '2026-27'}
```

Running `derive_current_season()` today (Sep 13, 2026) correctly reports `2026-27` and the training window slides to include all four relevant seasons.

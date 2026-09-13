# Fix sync_pipeline.py Season Derivation — Root Cause Fix

## Problem

`sync_pipeline.py` line 80 hardcodes `season_code="2526"` and `season_label="2025-26"`. `ingestion.py` line 22-27 hardcodes `DEFAULT_SEASONS` ending at `2025-26`. Every manual roster patch applied during this session is a symptom of the pipeline never crossing the season boundary automatically.

## Proposed Changes

### Season Derivation Module

#### [NEW] [`ml/data/season.py`](file:///d:/Yash Kokane/Projects/MatchSense/ml/data/season.py)

Single source of truth for season identification. Two derivation strategies layered defensively:

```python
def derive_current_season(now: datetime | None = None) -> tuple[str, str]:
    """Return (season_code, season_label) for the active PL season.
    
    Rule: PL seasons run Aug–May.
      month >= 8 → current year / (year+1)   e.g. Sep 2026 → ("2627", "2026-27")
      month <  8 → (year-1) / current year   e.g. Mar 2027 → ("2627", "2026-27")
    """
```

```python
def derive_training_window(current_code: str, window_size: int = 4) -> list[dict[str, str]]:
    """Return the 4-season sliding window ending at the current season.
    
    e.g. current="2627" → ["2324", "2425", "2526", "2627"]
    """
```

This is pure date arithmetic, no network calls, deterministically testable.

---

### Sync Pipeline Update

#### [MODIFY] [`scripts/sync_pipeline.py`](file:///d:/Yash Kokane/Projects/MatchSense/scripts/sync_pipeline.py)

- `run_phase_a_ingestion()` defaults change from hardcoded literals to `derive_current_season()`:
  ```python
  def run_phase_a_ingestion(
      session: Session,
      api_key: str = "",
      season_code: str | None = None,   # ← was "2526"
      season_label: str | None = None,   # ← was "2025-26"
  ) -> list[dict]:
      if season_code is None or season_label is None:
          season_code, season_label = derive_current_season()
  ```
- `main()` no longer passes hardcoded values — it relies on the dynamic defaults.
- **After** Phase A ingestion, add a log line confirming which season was derived: `logger.info("Derived active season: %s (%s)", season_label, season_code)`

---

### Ingestion Module Update

#### [MODIFY] [`ml/data/ingestion.py`](file:///d:/Yash Kokane/Projects/MatchSense/ml/data/ingestion.py)

- `DEFAULT_SEASONS` becomes a function `default_training_seasons()` that calls `derive_training_window()`:
  ```python
  def default_training_seasons() -> list[dict[str, str]]:
      from ml.data.season import derive_current_season, derive_training_window
      code, _ = derive_current_season()
      return derive_training_window(code, window_size=4)
  ```
- `load_all_seasons()` calls `default_training_seasons()` when `seasons is None` instead of reading the old constant.
- The old `DEFAULT_SEASONS` constant is **kept but deprecated** with a comment pointing to the function, so existing test code that imports it doesn't break.

---

### Tests

#### [NEW] `tests/unit/test_season.py`

Unit tests for the season derivation logic:

| Test | Input | Expected |
|---|---|---|
| September 2026 | `datetime(2026, 9, 13)` | `("2627", "2026-27")` |
| March 2027 | `datetime(2027, 3, 15)` | `("2627", "2026-27")` |
| August 2025 | `datetime(2025, 8, 1)` | `("2526", "2025-26")` |
| July 2026 (pre-season) | `datetime(2026, 7, 31)` | `("2526", "2025-26")` |
| Training window for "2627" | `derive_training_window("2627", 4)` | `[2324, 2425, 2526, 2627]` |
| Training window for "2526" | `derive_training_window("2526", 4)` | `[2223, 2324, 2425, 2526]` |

#### [MODIFY] `tests/integration/test_sync_pipeline.py`

- Import and verify that `run_phase_a_ingestion` with `season_code=None` resolves to the derived season, not `"2526"`.

---

### Git Commit Strategy

> [!IMPORTANT]
> Two separate commits, in order:

1. **`fix(pipeline): derive season dynamically from system date instead of hardcoded "2526"`**
   - `ml/data/season.py` (new)
   - `scripts/sync_pipeline.py` (modified)
   - `ml/data/ingestion.py` (modified)
   - `tests/unit/test_season.py` (new)
   - `tests/integration/test_sync_pipeline.py` (modified)

2. **`fix(data): correct 2026-27 roster — Coventry, Hull, Ipswich active; West Ham, Wolves, Sunderland historical`**
   - `ml/data/normalization.py` (new — was only in working tree)
   - `ml/data/schemas.py` (modified)
   - `frontend/src/lib/constants.ts` (modified)
   - `backend/services/prediction.py` (modified)
   - `backend/api/routes/predictions.py` (modified)
   - `ml/data/ingestion.py` (modified, if any remaining changes)

This ordering means: the root-cause fix lands first, then the roster correction is clearly the last manual patch — making it obvious to any future reader that commit 2 should never need to happen again because commit 1 makes it automatic.

---

## Verification Plan

### Automated Tests
```bash
uv run pytest tests/unit/test_season.py -v           # Season derivation unit tests
uv run pytest tests/integration/test_sync_pipeline.py -v  # Pipeline integration
uv run pytest tests/unit/ -q                          # Full backend regression
cd frontend && npm run test                           # Frontend regression
```

### Pipeline Dry-Run Verification
```bash
uv run python -c "from ml.data.season import derive_current_season, derive_training_window; print(derive_current_season()); print(derive_training_window(derive_current_season()[0]))"
```
Expected: `('2627', '2026-27')` and `[{'code': '2324', 'label': '2023-24'}, ..., {'code': '2627', 'label': '2026-27'}]`

## Open Questions

> [!NOTE]
> The `FootballDataClient.get_scheduled_fixtures()` already extracts `season.startDate`/`season.endDate` from the API response (lines 32-38 of `football_data_api.py`). Should we add a cross-check where, after Phase A ingestion, the pipeline compares its date-derived season against what the API actually returned, logging a warning if they disagree? This would catch edge cases like the PL season starting late or a summer tournament year pushing the schedule. It's a belt-and-suspenders addition — not blocking, but worth considering.

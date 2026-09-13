"""Weekly synchronization pipeline engine for MatchSense.

Orchestrates decoupled multi-phase execution:
- Phase A: Matches and upcoming fixtures ingestion (committed immediately).
- Gate 2B: Multi-gameweek out-of-sample audit against pre-match predictions.
- Phase B1: Dixon-Coles refit with 2-tier optimizer budget (Attempt 1 warm-start, Attempt 2 flat prior) + Gate 2A check.
- Phase B2: XGBoost refit + Gate 2A check + independent JSONB partial merge.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import pickle
import sys
import zlib
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.schemas import Fixture, Match, ModelArtifact
from ml.data.football_data_api import FootballDataClient
from ml.data.ingestion import download_season_csv, parse_season_csv
from ml.evaluation.metrics import compute_rps
from ml.models.dixon_coles import DixonColesModel
from ml.models.xgboost_model import XGBoostPredictor

logger = logging.getLogger("sync_pipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def check_gate_2a_dixon_coles(model: DixonColesModel) -> tuple[bool, str]:
    """Validate Dixon-Coles parameters against Gate 2A operational thresholds."""
    converged = getattr(model, "converged_", getattr(model, "_converged", False))
    if not converged:
        msg = getattr(model, "_convergence_message", "non-converged")
        return False, f"Optimizer did not converge: {msg}"

    home_adv = getattr(model, "home_adv_", getattr(model, "_home_advantage", None))
    if home_adv is None or not (1.05 <= home_adv <= 1.55):
        return False, f"home_advantage {home_adv} outside Gate 2A range [1.05, 1.55]"

    rho = getattr(model, "rho_", getattr(model, "_rho", None))
    if rho is None or not (-0.25 <= rho <= 0.25):
        return False, f"rho {rho} outside Gate 2A range [-0.25, 0.25]"

    attacks = getattr(model, "attack_", getattr(model, "_attack", {}))
    for t, att in attacks.items():
        if not (0.15 <= att <= 4.0):
            return False, f"Team '{t}' attack strength {att} outside [0.15, 4.0]"

    defenses = getattr(model, "defense_", getattr(model, "_defense", {}))
    for t, deff in defenses.items():
        if not (0.15 <= deff <= 4.0):
            return False, f"Team '{t}' defense strength {deff} outside [0.15, 4.0]"

    return True, "Gate 2A passed"


def check_gate_2a_xgboost(probs: dict[str, float]) -> tuple[bool, str]:
    """Validate XGBoost sample probabilities against Gate 2A operational thresholds."""
    total = probs.get("prob_home", 0.0) + probs.get("prob_draw", 0.0) + probs.get("prob_away", 0.0)
    if abs(total - 1.0) > 0.02:
        return False, f"XGBoost probabilities sum to {total}, expected 1.0"
    for k in ["prob_home", "prob_draw", "prob_away"]:
        val = probs.get(k, -1.0)
        if not (0.0 <= val <= 1.0):
            return False, f"XGBoost probability {k}={val} outside [0, 1]"
    return True, "Gate 2A passed"


def run_phase_a_ingestion(
    session: Session,
    api_key: str = "",
    season_code: str = "2526",
    season_label: str = "2025-26",
) -> list[dict]:
    """Ingest latest completed matches and upcoming fixtures into DB. Returns new completed matches."""
    logger.info("=== Phase A: Ingesting Ground-Truth Matches & Upcoming Schedules ===")

    # 1. Fetch CSV
    new_matches = []
    try:
        csv_str = download_season_csv(season_code)
        df_matches = parse_season_csv(csv_str, season_label)

        for _, row in df_matches.iterrows():
            match_date = pd.to_datetime(row["Date"]).date()
            exists = session.query(Match).filter_by(
                season=season_label,
                date=match_date,
                home_team=row["HomeTeam"],
                away_team=row["AwayTeam"],
            ).first()
            if not exists:
                m = Match(
                    season=season_label,
                    date=match_date,
                    home_team=row["HomeTeam"],
                    away_team=row["AwayTeam"],
                    home_goals=int(row["FTHG"]),
                    away_goals=int(row["FTAG"]),
                    result=row["FTR"],
                    ht_home_goals=int(row["HTHG"]) if pd.notna(row.get("HTHG")) else None,
                    ht_away_goals=int(row["HTAG"]) if pd.notna(row.get("HTAG")) else None,
                    home_shots=int(row["HS"]) if pd.notna(row.get("HS")) else None,
                    away_shots=int(row["AS"]) if pd.notna(row.get("AS")) else None,
                    home_shots_on_target=int(row["HST"]) if pd.notna(row.get("HST")) else None,
                    away_shots_on_target=int(row["AST"]) if pd.notna(row.get("AST")) else None,
                    avg_odds_home=float(row["AvgH"]) if pd.notna(row.get("AvgH")) else None,
                    avg_odds_draw=float(row["AvgD"]) if pd.notna(row.get("AvgD")) else None,
                    avg_odds_away=float(row["AvgA"]) if pd.notna(row.get("AvgA")) else None,
                )
                session.add(m)
                new_matches.append({
                    "season": season_label,
                    "date": row["Date"],
                    "home_team": row["HomeTeam"],
                    "away_team": row["AwayTeam"],
                    "result": row["FTR"],
                    "gameweek": 28,
                })
    except Exception as e:
        logger.warning("Failed to fetch or parse season CSV: %s", e)

    # 2. Fetch upcoming fixtures
    client = FootballDataClient(api_key=api_key)
    try:
        fixtures_data = client.get_scheduled_fixtures()
        for f in fixtures_data:
            existing_f = session.query(Fixture).filter_by(id=f["id"]).first()
            kickoff = pd.to_datetime(f["kickoff_time"]).to_pydatetime()
            if not existing_f:
                session.add(
                    Fixture(
                        id=f["id"],
                        season=f["season"],
                        gameweek=f["gameweek"],
                        kickoff_time=kickoff,
                        home_team=f["home_team"],
                        away_team=f["away_team"],
                        status=f["status"],
                        precomputed_predictions={},
                    )
                )
            else:
                existing_f.kickoff_time = kickoff
                existing_f.gameweek = f["gameweek"]
                existing_f.status = f["status"]
    except Exception as e:
        logger.warning("Failed to fetch Football-Data.org fixtures: %s", e)

    session.commit()
    logger.info("Phase A committed successfully. Ingested %d new matches.", len(new_matches))
    return new_matches


def score_gate_2b_audit(completed_matches: list[dict], pre_match_preds: dict) -> list[dict]:
    """Score completed matches against pre-match fixture predictions grouped by GW."""
    if not completed_matches:
        return []

    gws = sorted(list(set(m.get("gameweek", 28) for m in completed_matches)))
    audit_cards = []

    for gw in gws:
        gw_matches = [m for m in completed_matches if m.get("gameweek", 28) == gw]
        dc_rps_list, xgb_rps_list = [], []
        dc_correct, xgb_correct = 0, 0

        for m in gw_matches:
            pair = (m["home_team"], m["away_team"])
            res = m["result"]
            actual = [1.0 if res == "H" else 0.0, 1.0 if res == "D" else 0.0, 1.0 if res == "A" else 0.0]

            if pair in pre_match_preds:
                dc_p = pre_match_preds[pair].get("dixon_coles")
                if dc_p:
                    p = [dc_p["prob_home"], dc_p["prob_draw"], dc_p["prob_away"]]
                    val = float(compute_rps(np.array([p]), np.array([actual]))[0])
                    dc_rps_list.append(val)
                    if ["H", "D", "A"][p.index(max(p))] == res:
                        dc_correct += 1

                xgb_p = pre_match_preds[pair].get("xgboost")
                if xgb_p:
                    p = [xgb_p["prob_home"], xgb_p["prob_draw"], xgb_p["prob_away"]]
                    val = float(compute_rps(np.array([p]), np.array([actual]))[0])
                    xgb_rps_list.append(val)
                    if ["H", "D", "A"][p.index(max(p))] == res:
                        xgb_correct += 1

        avg_dc_rps = round(sum(dc_rps_list) / len(dc_rps_list), 4) if dc_rps_list else None
        avg_xgb_rps = round(sum(xgb_rps_list) / len(xgb_rps_list), 4) if xgb_rps_list else None

        if avg_dc_rps and avg_dc_rps > 0.240:
            logger.warning("CRITICAL: Dixon-Coles Gate 2B RPS %.4f exceeded threshold 0.240 for GW %s", avg_dc_rps, gw)
        if avg_xgb_rps and avg_xgb_rps > 0.240:
            logger.warning("CRITICAL: XGBoost Gate 2B RPS %.4f exceeded threshold 0.240 for GW %s", avg_xgb_rps, gw)

        audit_cards.append({
            "gameweek": int(gw),
            "n_matches": len(gw_matches),
            "dixon_coles_rps": avg_dc_rps,
            "xgboost_rps": avg_xgb_rps,
            "dixon_coles_acc": round(dc_correct / len(gw_matches), 4) if gw_matches else 0.0,
            "xgboost_acc": round(xgb_correct / len(gw_matches), 4) if gw_matches else 0.0,
            "scored_at": datetime.now(timezone.utc).isoformat(),
        })

    return audit_cards


def _update_fixture_predictions_atomic(session: Session, fixture_id: int, model_name: str, payload: dict) -> None:
    """Update fixture precomputed_predictions using jsonb_set on Postgres, or dict merge on SQLite."""
    dialect_name = session.bind.dialect.name if session.bind else "sqlite"
    now_utc = datetime.now(timezone.utc)

    if dialect_name == "postgresql":
        stmt = text("""
            UPDATE fixtures
            SET precomputed_predictions = jsonb_set(
                COALESCE(precomputed_predictions, '{}'::jsonb),
                :path,
                CAST(:payload AS jsonb),
                true
            ),
            updated_at = :now
            WHERE id = :fixture_id
        """)
        session.execute(stmt, {
            "path": f"{{{model_name}}}",
            "payload": json.dumps(payload),
            "now": now_utc,
            "fixture_id": fixture_id,
        })
    else:
        fix = session.query(Fixture).filter_by(id=fixture_id).one()
        preds = dict(fix.precomputed_predictions or {})
        preds[model_name] = payload
        fix.precomputed_predictions = preds
        fix.updated_at = now_utc


def run_phase_b1_dixon_coles(
    session: Session,
    fixture_predictions: dict[int, dict] | None = None,
    dry_run_only: bool = False,
    matches_df: pd.DataFrame | None = None,
) -> bool:
    """Refit Dixon-Coles with 2-tier budget, enforce Gate 2A, update DB atomically."""
    logger.info("=== Phase B1: Dixon-Coles Optimization & Activation ===")
    try:
        model = None
        new_version = f"dc_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        if not dry_run_only and matches_df is not None:
            # 1. Check for prior active model to warm-start
            active_row = session.query(ModelArtifact).filter_by(model_name="dixon_coles", is_active=True).first()
            warm_params = None
            if active_row:
                try:
                    decompressed = zlib.decompress(active_row.artifact_bytes)
                    prior_model = pickle.loads(decompressed)
                    warm_params = getattr(prior_model, "get_params_vector", lambda: None)()
                except Exception as e:
                    logger.warning("Could not extract warm start params from active Dixon-Coles model: %s", e)

            # Attempt 1: Warm start
            logger.info("Dixon-Coles Attempt 1: warm-start fit (maxfun=50,000)")
            model = DixonColesModel(xi=0.005)
            model.fit(matches_df, warm_start_params=warm_params)
            passed, reason = check_gate_2a_dixon_coles(model)

            # Attempt 2: Flat prior reset if Attempt 1 failed
            if not passed:
                logger.warning("Attempt 1 failed Gate 2A (%s). Triggering Attempt 2: flat prior reset (maxfun=100,000)", reason)
                model = DixonColesModel(xi=0.005)
                model.fit(matches_df, warm_start_params=None)
                passed, reason = check_gate_2a_dixon_coles(model)

            if not passed:
                logger.error("Dixon-Coles failed Gate 2A after retry: %s. Aborting Phase B1.", reason)
                session.rollback()
                return False

            # Gate 2A passed: deactivate old and insert new model
            session.query(ModelArtifact).filter_by(model_name="dixon_coles", is_active=True).update({"is_active": False})
            compressed = zlib.compress(pickle.dumps(model))
            artifact = ModelArtifact(
                model_name="dixon_coles",
                version=new_version,
                is_active=True,
                manifest=model.get_model_info(),
                artifact_bytes=compressed,
            )
            session.add(artifact)

        # Update fixtures using atomic jsonb_set with COALESCE
        if fixture_predictions:
            for fix_id, payload in fixture_predictions.items():
                _update_fixture_predictions_atomic(session, fix_id, "dixon_coles", payload)
        elif model is not None:
            fixtures = session.query(Fixture).filter(Fixture.status.in_(["SCHEDULED", "TIMED"])).all()
            for fix in fixtures:
                try:
                    proba = model.predict_proba(fix.home_team, fix.away_team)
                    score = model.predict_most_likely_score(fix.home_team, fix.away_team)
                    dist = model.predict_score_distribution(fix.home_team, fix.away_team)
                    payload = {
                        "model_version": new_version,
                        "computed_at": datetime.now(timezone.utc).isoformat(),
                        "prob_home": round(proba["prob_home"], 4),
                        "prob_draw": round(proba["prob_draw"], 4),
                        "prob_away": round(proba["prob_away"], 4),
                        "predicted_score": {"home": score[0], "away": score[1]},
                        "score_distribution": dist.tolist(),
                    }
                    _update_fixture_predictions_atomic(session, fix.id, "dixon_coles", payload)
                except Exception as e:
                    logger.warning("Could not predict fixture %s (%s vs %s): %s", fix.id, fix.home_team, fix.away_team, e)

        return True
    except Exception as e:
        logger.error("Phase B1 failed: %s. Rolling back.", e)
        session.rollback()
        return False


def run_phase_b2_xgboost(
    session: Session,
    fixture_predictions: dict[int, dict] | None = None,
    dry_run_only: bool = False,
    matches_df: pd.DataFrame | None = None,
) -> bool:
    """Refit XGBoost, enforce Gate 2A, update DB atomically."""
    logger.info("=== Phase B2: XGBoost Optimization & Activation ===")
    try:
        model = None
        new_version = f"xgb_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        if not dry_run_only and matches_df is not None:
            logger.info("Fitting XGBoostPredictor on matches window")
            model = XGBoostPredictor()
            model.fit(matches_df)

            # Gate 2A sanity check
            test_home = matches_df["HomeTeam"].iloc[-1]
            test_away = matches_df["AwayTeam"].iloc[-1]
            sample_proba = model.predict_proba(test_home, test_away)
            passed, reason = check_gate_2a_xgboost(sample_proba)
            if not passed:
                logger.error("XGBoost failed Gate 2A: %s. Aborting Phase B2.", reason)
                session.rollback()
                return False

            session.query(ModelArtifact).filter_by(model_name="xgboost", is_active=True).update({"is_active": False})
            compressed = zlib.compress(pickle.dumps(model))
            artifact = ModelArtifact(
                model_name="xgboost",
                version=new_version,
                is_active=True,
                manifest=model.get_model_info(),
                artifact_bytes=compressed,
            )
            session.add(artifact)

        # Update fixtures using atomic jsonb_set with COALESCE
        if fixture_predictions:
            for fix_id, payload in fixture_predictions.items():
                _update_fixture_predictions_atomic(session, fix_id, "xgboost", payload)
        elif model is not None:
            fixtures = session.query(Fixture).filter(Fixture.status.in_(["SCHEDULED", "TIMED"])).all()
            for fix in fixtures:
                try:
                    proba = model.predict_proba(fix.home_team, fix.away_team)
                    payload = {
                        "model_version": new_version,
                        "computed_at": datetime.now(timezone.utc).isoformat(),
                        "prob_home": round(proba["prob_home"], 4),
                        "prob_draw": round(proba["prob_draw"], 4),
                        "prob_away": round(proba["prob_away"], 4),
                        "predicted_score": None,
                        "score_distribution": None,
                    }
                    _update_fixture_predictions_atomic(session, fix.id, "xgboost", payload)
                except Exception as e:
                    logger.warning("Could not predict fixture %s (%s vs %s): %s", fix.id, fix.home_team, fix.away_team, e)

        return True
    except Exception as e:
        logger.error("Phase B2 failed: %s. Rolling back.", e)
        session.rollback()
        return False


def main():
    logger.info("Starting weekly synchronization pipeline run.")
    with SessionLocal() as session:
        # Phase A: Factual ingestion (committed immediately)
        new_matches = run_phase_a_ingestion(session, api_key=settings.football_data_api_key)

        # Gate 2B: Audit scoring
        # Load pre-match predictions from fixtures that recently finished
        logger.info("Phase A complete. Proceeding to Model Training phases.")

        # Phase B1: Dixon-Coles
        b1_ok = run_phase_b1_dixon_coles(session)
        if b1_ok:
            session.commit()
            logger.info("Phase B1 committed successfully.")
        else:
            session.rollback()
            logger.warning("Phase B1 failed. Retained active Dixon-Coles model.")

        # Phase B2: XGBoost
        b2_ok = run_phase_b2_xgboost(session)
        if b2_ok:
            session.commit()
            logger.info("Phase B2 committed successfully.")
        else:
            session.rollback()
            logger.warning("Phase B2 failed. Retained active XGBoost model.")

    logger.info("Weekly synchronization finished.")


if __name__ == "__main__":
    main()

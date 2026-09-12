"""Seed data script: download historical data, validate, fit model.

Usage:
    uv run python scripts/seed_data.py

This script:
1. Downloads 4 seasons of Premier League data from football-data.co.uk
2. Validates with Pandera schemas
3. Fits the Dixon-Coles model
4. Saves the fitted model to disk
"""

import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ml.data.ingestion import load_all_seasons
from ml.data.schemas import raw_match_schema
from ml.models.dixon_coles import DixonColesModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Download data, validate, fit model, and save."""
    project_root = Path(__file__).parent.parent
    cache_dir = project_root / "data" / "raw"
    model_dir = project_root / "data" / "models"

    # Step 1: Download and parse all seasons
    logger.info("=== Step 1: Loading match data ===")
    matches = load_all_seasons(cache_dir=cache_dir)
    logger.info("Loaded %d matches", len(matches))

    # Step 2: Validate with Pandera
    logger.info("=== Step 2: Validating data ===")
    try:
        raw_match_schema.validate(matches, lazy=True)
        logger.info("Data validation passed ✓")
    except Exception as e:
        logger.error("Data validation failed: %s", e)
        raise

    # Step 3: Fit Dixon-Coles model
    logger.info("=== Step 3: Fitting Dixon-Coles model ===")
    model = DixonColesModel(xi=0.005)
    model.fit(matches)

    info = model.get_model_info()
    logger.info("Model info: %s", info)

    # Step 4: Quick sanity checks
    logger.info("=== Step 4: Sanity checks ===")
    strengths = model.get_team_strengths()

    # Print top 5 attack strengths
    sorted_attack = sorted(strengths.items(), key=lambda x: x[1]["attack"], reverse=True)
    logger.info("Top 5 attack strengths:")
    for team, s in sorted_attack[:5]:
        logger.info("  %s: attack=%.3f, defense=%.3f", team, s["attack"], s["defense"])

    # Test a prediction
    top_team = sorted_attack[0][0]
    bottom_team = sorted_attack[-1][0]
    proba = model.predict_proba(top_team, bottom_team)
    score = model.predict_most_likely_score(top_team, bottom_team)
    logger.info(
        "Sample prediction: %s vs %s → P(H)=%.2f, P(D)=%.2f, P(A)=%.2f, Score=%d-%d",
        top_team, bottom_team,
        proba["prob_home"], proba["prob_draw"], proba["prob_away"],
        score[0], score[1],
    )

    # Verify probabilities sum to 1
    total = proba["prob_home"] + proba["prob_draw"] + proba["prob_away"]
    assert abs(total - 1.0) < 0.01, f"Probabilities don't sum to 1: {total}"
    logger.info("Probability sum check passed ✓ (sum=%.4f)", total)

    # Verify home advantage > 1
    assert model._home_advantage > 1.0, (
        f"Home advantage should be > 1.0, got {model._home_advantage}"
    )
    logger.info("Home advantage check passed ✓ (gamma=%.3f)", model._home_advantage)

    # Step 5: Save model
    logger.info("=== Step 5: Saving model ===")
    model_path = model_dir / "dixon_coles_latest.pkl"
    model.save(model_path)
    logger.info("Model saved to %s", model_path)

    logger.info("=== Done! MatchSense is ready. ===")
    logger.info("Start the API with: uv run uvicorn backend.api.main:app --reload")


if __name__ == "__main__":
    main()

"""End-to-end integration tests for the MatchSense pipeline.

Tests the full lifecycle:
1. Ingest CSV data
2. Validate with Pandera
3. Persist to database
4. Read back from database
5. Compute match features
6. Fit Dixon-Coles model
7. Generate predictions
"""

import sys
from pathlib import Path

# Ensure MatchSense root is in sys.path when running from any working directory
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.database import Base
from backend.services.prediction import PredictionService
from ml.data.ingestion import parse_season_csv
from ml.data.loader import load_matches_from_db, save_matches_to_db
from ml.data.schemas import raw_match_schema
from ml.features.pipeline import build_match_features
from ml.models.dixon_coles import DixonColesModel

INTEGRATION_CSV = """Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HTR,AvgH,AvgD,AvgA
E0,12/08/2023,Arsenal,Nott'm Forest,2,1,H,2,0,H,1.20,7.00,14.00
E0,12/08/2023,Bournemouth,West Ham,1,1,D,0,0,D,2.70,3.50,2.60
E0,12/08/2023,Brighton,Luton,4,1,H,1,0,H,1.33,5.50,9.00
E0,12/08/2023,Everton,Fulham,0,1,A,0,0,D,2.20,3.30,3.40
E0,12/08/2023,Sheffield United,Crystal Palace,0,1,A,0,0,D,3.00,3.20,2.50
E0,12/08/2023,Newcastle,Aston Villa,5,1,H,2,1,H,1.75,3.90,4.60
E0,13/08/2023,Brentford,Tottenham,2,2,D,2,2,D,2.80,3.60,2.50
E0,13/08/2023,Chelsea,Liverpool,1,1,D,1,1,D,2.90,3.60,2.40
E0,14/08/2023,Man United,Wolves,1,0,H,0,0,D,1.33,5.50,9.00
E0,19/08/2023,Liverpool,Bournemouth,3,1,H,2,1,H,1.22,7.00,12.00
E0,19/08/2023,Wolves,Brighton,1,4,A,0,1,A,3.80,3.70,1.95
E0,19/08/2023,Tottenham,Man United,2,0,H,0,0,D,2.80,3.60,2.45
E0,19/08/2023,Man City,Newcastle,1,0,H,1,0,H,1.65,4.20,5.00
E0,20/08/2023,Aston Villa,Everton,4,0,H,2,0,H,1.70,4.00,4.80
E0,20/08/2023,West Ham,Chelsea,3,1,H,1,1,D,3.60,3.60,2.05
E0,21/08/2023,Crystal Palace,Arsenal,0,1,A,0,0,D,5.75,4.00,1.60
"""


@pytest.fixture
def test_db():
    """In-memory SQLite database session for isolated testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


class TestFullPipeline:
    """Integration test suite executing the entire MatchSense workflow."""

    def test_end_to_end_pipeline(self, test_db):
        # 1. Ingestion
        df = parse_season_csv(INTEGRATION_CSV, season_label="2023-24")
        assert len(df) == 16
        assert df["Season"].iloc[0] == "2023-24"

        # 2. Validation
        validated = raw_match_schema.validate(df)
        assert len(validated) == 16

        # 3. Database persistence
        inserted = save_matches_to_db(test_db, df)
        assert inserted == 16

        # Idempotency check — second save should insert 0 new records
        inserted_again = save_matches_to_db(test_db, df)
        assert inserted_again == 0

        # 4. Read back from database
        db_df = load_matches_from_db(test_db, season="2023-24")
        assert len(db_df) == 16
        assert "Arsenal" in db_df["HomeTeam"].values
        assert "Manchester Utd" in db_df["HomeTeam"].values

        # 5. Feature Engineering
        features = build_match_features(
            matches=db_df,
            home_team="Arsenal",
            away_team="Liverpool",
            match_date=pd.Timestamp("2023-08-25"),
            season="2023-24",
            all_seasons=["2023-24"],
        )
        assert "home_matches_available" in features
        assert "away_matches_available" in features
        assert "h2h_total_matches" in features

        # 6. Fit Dixon-Coles model
        model = DixonColesModel(xi=0.005)
        model.fit(db_df)

        info = model.get_model_info()
        assert info["n_teams"] > 0
        assert info["n_matches"] == 16

        # 7. Predictions via PredictionService
        service = PredictionService(model=model)
        prediction = service.predict_match("Arsenal", "Liverpool")

        assert prediction["home_team"] == "Arsenal"
        assert prediction["away_team"] == "Liverpool"
        assert 0 <= prediction["prob_home"] <= 1
        assert 0 <= prediction["prob_draw"] <= 1
        assert 0 <= prediction["prob_away"] <= 1
        total_p = (
            prediction["prob_home"]
            + prediction["prob_draw"]
            + prediction["prob_away"]
        )
        assert total_p == pytest.approx(1.0, abs=0.02)
        assert prediction["predicted_score"]["home"] >= 0
        assert prediction["predicted_score"]["away"] >= 0
        assert len(prediction["score_distribution"]) > 0

"""Unit tests for data ingestion, normalization, and validation."""

import pandas as pd
import pandera as pa
import pytest

from ml.data.ingestion import (
    compute_implied_probabilities,
    normalize_team_name,
    parse_season_csv,
)
from ml.data.schemas import raw_match_schema

SAMPLE_CSV = """Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HTR,AvgH,AvgD,AvgA
E0,12/08/2023,Burnley,Man City,0,3,A,0,2,A,9.50,5.25,1.33
E0,12/08/23,Arsenal,Nott'm Forest,2,1,H,2,0,H,1.20,7.00,14.00
E0,13/08/2023,Chelsea,Liverpool,1,1,D,1,1,D,2.90,3.60,2.40
E0,14/08/23,Man United,Wolves,1,0,H,0,0,D,1.33,5.50,9.00
"""


class TestTeamNameNormalization:
    """Test mapping of raw names to canonical team names."""

    def test_known_mappings(self):
        assert normalize_team_name("Man United") == "Manchester Utd"
        assert normalize_team_name("Man City") == "Manchester City"
        assert normalize_team_name("Nott'm Forest") == "Nottingham Forest"
        assert normalize_team_name("Wolves") == "Wolverhampton"
        assert normalize_team_name("Spurs") == "Tottenham"
        assert normalize_team_name("Sheffield United") == "Sheffield Utd"

    def test_unmapped_name_preserved(self):
        assert normalize_team_name("Arsenal") == "Arsenal"
        assert normalize_team_name("Chelsea") == "Chelsea"
        assert normalize_team_name("Liverpool") == "Liverpool"


class TestCSVParser:
    """Test parsing and cleaning of football-data.co.uk CSVs."""

    def test_parse_season_csv_structure(self):
        df = parse_season_csv(SAMPLE_CSV, season_label="2023-24")

        assert len(df) == 4
        assert df["Season"].iloc[0] == "2023-24"
        assert "Manchester City" in df["AwayTeam"].values
        assert "Nottingham Forest" in df["AwayTeam"].values
        assert "Manchester Utd" in df["HomeTeam"].values
        assert "Wolverhampton" in df["AwayTeam"].values

    def test_date_parsing_both_formats(self):
        df = parse_season_csv(SAMPLE_CSV, season_label="2023-24")

        # 12/08/2023 (yyyy) and 12/08/23 (yy) should both parse to Aug 12, 2023
        assert df["Date"].iloc[0] == pd.Timestamp("2023-08-12")
        assert df["Date"].iloc[1] == pd.Timestamp("2023-08-12")
        assert df["Date"].iloc[2] == pd.Timestamp("2023-08-13")
        assert df["Date"].iloc[3] == pd.Timestamp("2023-08-14")


class TestImpliedProbabilities:
    """Test bookmaker implied odds calculation and overround removal."""

    def test_overround_removal(self):
        df = parse_season_csv(SAMPLE_CSV, season_label="2023-24")
        df_probs = compute_implied_probabilities(df)

        for _, row in df_probs.iterrows():
            total = (
                row["implied_prob_home"]
                + row["implied_prob_draw"]
                + row["implied_prob_away"]
            )
            assert total == pytest.approx(1.0, abs=1e-4)
            assert 0.0 < row["implied_prob_home"] < 1.0
            assert 0.0 < row["implied_prob_draw"] < 1.0
            assert 0.0 < row["implied_prob_away"] < 1.0

    def test_missing_odds_columns(self):
        df = pd.DataFrame({
            "Date": [pd.Timestamp("2024-01-01")],
            "HomeTeam": ["Arsenal"],
            "AwayTeam": ["Chelsea"],
            "FTHG": [1],
            "FTAG": [0],
            "FTR": ["H"],
            "Season": ["2023-24"],
        })
        result = compute_implied_probabilities(df)
        assert result["implied_prob_home"].iloc[0] is None


class TestPanderaValidation:
    """Test Pandera schema validation on match data."""

    def test_valid_data_passes(self):
        df = parse_season_csv(SAMPLE_CSV, season_label="2023-24")
        validated = raw_match_schema.validate(df)
        assert len(validated) == 4

    def test_negative_goals_fails(self):
        df = parse_season_csv(SAMPLE_CSV, season_label="2023-24")
        df.loc[0, "FTHG"] = -1
        with pytest.raises(pa.errors.SchemaError):
            raw_match_schema.validate(df)

    def test_inconsistent_ftr_fails(self):
        df = parse_season_csv(SAMPLE_CSV, season_label="2023-24")
        # 0-3 match, set FTR to 'H'
        df.loc[0, "FTR"] = "H"
        with pytest.raises(pa.errors.SchemaError):
            raw_match_schema.validate(df)

    def test_missing_required_column_fails(self):
        df = parse_season_csv(SAMPLE_CSV, season_label="2023-24")
        df_missing = df.drop(columns=["HomeTeam"])
        with pytest.raises(pa.errors.SchemaError):
            raw_match_schema.validate(df_missing)

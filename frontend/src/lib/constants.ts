export interface TeamMeta {
  name: string;
  shortName: string;
  primaryColor: string;
}

export const PREMIER_LEAGUE_TEAMS: Record<string, TeamMeta> = {
  "Arsenal": { name: "Arsenal", shortName: "ARS", primaryColor: "#EF0107" },
  "Aston Villa": { name: "Aston Villa", shortName: "AVL", primaryColor: "#95BFE5" },
  "Bournemouth": { name: "Bournemouth", shortName: "BOU", primaryColor: "#DA291C" },
  "Brentford": { name: "Brentford", shortName: "BRE", primaryColor: "#E30613" },
  "Brighton": { name: "Brighton", shortName: "BHA", primaryColor: "#0057B8" },
  "Chelsea": { name: "Chelsea", shortName: "CHE", primaryColor: "#034694" },
  "Crystal Palace": { name: "Crystal Palace", shortName: "CRY", primaryColor: "#1B458F" },
  "Everton": { name: "Everton", shortName: "EVE", primaryColor: "#003399" },
  "Fulham": { name: "Fulham", shortName: "FUL", primaryColor: "#FFFFFF" },
  "Ipswich Town": { name: "Ipswich Town", shortName: "IPS", primaryColor: "#003399" },
  "Leicester City": { name: "Leicester City", shortName: "LEI", primaryColor: "#003090" },
  "Liverpool": { name: "Liverpool", shortName: "LIV", primaryColor: "#C8102E" },
  "Manchester City": { name: "Manchester City", shortName: "MCI", primaryColor: "#6CABDD" },
  "Manchester United": { name: "Manchester United", shortName: "MUN", primaryColor: "#DA291C" },
  "Newcastle United": { name: "Newcastle United", shortName: "NEW", primaryColor: "#241F20" },
  "Nottingham Forest": { name: "Nottingham Forest", shortName: "NFO", primaryColor: "#DD0000" },
  "Southampton": { name: "Southampton", shortName: "SOU", primaryColor: "#D71920" },
  "Tottenham Hotspur": { name: "Tottenham Hotspur", shortName: "TOT", primaryColor: "#132257" },
  "West Ham United": { name: "West Ham United", shortName: "WHU", primaryColor: "#7A263A" },
};

import type { FixtureCard } from "@/types";

export const MOCK_FIXTURES_GW28: FixtureCard[] = [
  {
    id: 1,
    gameweek: 28,
    kickoff_time: "2026-09-19T14:00:00Z",
    home_team: "Arsenal",
    away_team: "Chelsea",
    status: "SCHEDULED",
    predictions: {
      dixon_coles: { prob_home: 0.52, prob_draw: 0.25, prob_away: 0.23 },
      xgboost: { prob_home: 0.49, prob_draw: 0.27, prob_away: 0.24 },
    },
  },
  {
    id: 2,
    gameweek: 28,
    kickoff_time: "2026-09-19T16:30:00Z",
    home_team: "Manchester City",
    away_team: "Liverpool",
    status: "SCHEDULED",
    predictions: {
      dixon_coles: { prob_home: 0.45, prob_draw: 0.28, prob_away: 0.27 },
      xgboost: { prob_home: 0.48, prob_draw: 0.26, prob_away: 0.26 },
    },
  },
  {
    id: 3,
    gameweek: 28,
    kickoff_time: "2026-09-20T13:00:00Z",
    home_team: "Tottenham Hotspur",
    away_team: "Aston Villa",
    status: "SCHEDULED",
    predictions: {
      dixon_coles: { prob_home: 0.42, prob_draw: 0.29, prob_away: 0.29 },
      xgboost: { prob_home: 0.44, prob_draw: 0.28, prob_away: 0.28 },
    },
  },
  {
    id: 4,
    gameweek: 28,
    kickoff_time: "2026-09-20T15:30:00Z",
    home_team: "Newcastle United",
    away_team: "Manchester United",
    status: "SCHEDULED",
    predictions: {
      dixon_coles: { prob_home: 0.41, prob_draw: 0.28, prob_away: 0.31 },
      xgboost: { prob_home: 0.43, prob_draw: 0.27, prob_away: 0.30 },
    },
  },
  {
    id: 5,
    gameweek: 28,
    kickoff_time: "2026-09-20T18:00:00Z",
    home_team: "Brighton",
    away_team: "West Ham United",
    status: "SCHEDULED",
    predictions: {
      dixon_coles: { prob_home: 0.47, prob_draw: 0.27, prob_away: 0.26 },
      xgboost: { prob_home: 0.46, prob_draw: 0.28, prob_away: 0.26 },
    },
  },
  {
    id: 6,
    gameweek: 28,
    kickoff_time: "2026-09-21T19:00:00Z",
    home_team: "Everton",
    away_team: "Fulham",
    status: "SCHEDULED",
    predictions: {
      dixon_coles: { prob_home: 0.39, prob_draw: 0.31, prob_away: 0.30 },
      xgboost: { prob_home: 0.38, prob_draw: 0.32, prob_away: 0.30 },
    },
  },
];

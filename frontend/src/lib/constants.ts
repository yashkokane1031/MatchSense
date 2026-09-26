export interface TeamMeta {
  name: string;
  shortName: string;
  primaryColor: string;
}

export const ALIAS_LOOKUP: Record<string, string> = {
  // Leeds
  "Leeds": "Leeds United",
  "Leeds United FC": "Leeds United",
  "Leeds Utd": "Leeds United",

  // Manchester clubs
  "Manchester Utd": "Manchester United",
  "Man United": "Manchester United",
  "Man Utd": "Manchester United",
  "Manchester United FC": "Manchester United",
  "Man City": "Manchester City",
  "Manchester City FC": "Manchester City",

  // Tottenham
  "Tottenham": "Tottenham Hotspur",
  "Spurs": "Tottenham Hotspur",
  "Tottenham Hotspur FC": "Tottenham Hotspur",

  // Newcastle
  "Newcastle": "Newcastle United",
  "Newcastle United FC": "Newcastle United",

  // West Ham
  "West Ham": "West Ham United",
  "West Ham United FC": "West Ham United",

  // Wolverhampton
  "Wolverhampton": "Wolverhampton Wanderers",
  "Wolves": "Wolverhampton Wanderers",
  "Wolverhampton Wanderers FC": "Wolverhampton Wanderers",

  // Leicester
  "Leicester": "Leicester City",
  "Leicester City FC": "Leicester City",

  // Ipswich
  "Ipswich": "Ipswich Town",
  "Ipswich Town FC": "Ipswich Town",

  // Coventry
  "Coventry": "Coventry City",
  "Coventry City FC": "Coventry City",

  // Hull
  "Hull": "Hull City",
  "Hull City FC": "Hull City",
  "Hull City AFC": "Hull City",

  // Sheffield United
  "Sheffield Utd": "Sheffield United",
  "Sheffield United FC": "Sheffield United",

  // Luton
  "Luton": "Luton Town",
  "Luton Town FC": "Luton Town",

  // Brighton
  "Brighton & Hove Albion": "Brighton",
  "Brighton and Hove Albion": "Brighton",
  "Brighton & Hove Albion FC": "Brighton",

  // Bournemouth
  "AFC Bournemouth": "Bournemouth",

  // Nottingham Forest
  "Nott'm Forest": "Nottingham Forest",
  "Nottingham Forest FC": "Nottingham Forest",

  // Sunderland
  "Sunderland AFC": "Sunderland",
  "Sunderland FC": "Sunderland",

  // Burnley
  "Burnley FC": "Burnley",

  // Common FC suffixes
  "Arsenal FC": "Arsenal",
  "Aston Villa FC": "Aston Villa",
  "Brentford FC": "Brentford",
  "Chelsea FC": "Chelsea",
  "Crystal Palace FC": "Crystal Palace",
  "Everton FC": "Everton",
  "Fulham FC": "Fulham",
  "Liverpool FC": "Liverpool",
  "Southampton FC": "Southampton",
};

export const ALL_PREMIER_LEAGUE_TEAMS: Record<string, TeamMeta> = {
  "Arsenal": { name: "Arsenal", shortName: "ARS", primaryColor: "#EF0107" },
  "Aston Villa": { name: "Aston Villa", shortName: "AVL", primaryColor: "#95BFE5" },
  "Bournemouth": { name: "Bournemouth", shortName: "BOU", primaryColor: "#DA291C" },
  "Brentford": { name: "Brentford", shortName: "BRE", primaryColor: "#E30613" },
  "Brighton": { name: "Brighton", shortName: "BHA", primaryColor: "#0057B8" },
  "Burnley": { name: "Burnley", shortName: "BUR", primaryColor: "#6C1D45" },
  "Chelsea": { name: "Chelsea", shortName: "CHE", primaryColor: "#034694" },
  "Coventry City": { name: "Coventry City", shortName: "COV", primaryColor: "#00A3E0" },
  "Crystal Palace": { name: "Crystal Palace", shortName: "CRY", primaryColor: "#1B458F" },
  "Everton": { name: "Everton", shortName: "EVE", primaryColor: "#003399" },
  "Fulham": { name: "Fulham", shortName: "FUL", primaryColor: "#FFFFFF" },
  "Hull City": { name: "Hull City", shortName: "HUL", primaryColor: "#F5A623" },
  "Ipswich Town": { name: "Ipswich Town", shortName: "IPS", primaryColor: "#003399" },
  "Leeds United": { name: "Leeds United", shortName: "LEE", primaryColor: "#FFCD00" },
  "Leicester City": { name: "Leicester City", shortName: "LEI", primaryColor: "#003090" },
  "Liverpool": { name: "Liverpool", shortName: "LIV", primaryColor: "#C8102E" },
  "Luton Town": { name: "Luton Town", shortName: "LUT", primaryColor: "#FF6600" },
  "Manchester City": { name: "Manchester City", shortName: "MCI", primaryColor: "#6CABDD" },
  "Manchester United": { name: "Manchester United", shortName: "MUN", primaryColor: "#DA291C" },
  "Newcastle United": { name: "Newcastle United", shortName: "NEW", primaryColor: "#241F20" },
  "Nottingham Forest": { name: "Nottingham Forest", shortName: "NFO", primaryColor: "#DD0000" },
  "Sheffield United": { name: "Sheffield United", shortName: "SHU", primaryColor: "#EE2737" },
  "Southampton": { name: "Southampton", shortName: "SOU", primaryColor: "#D71920" },
  "Sunderland": { name: "Sunderland", shortName: "SUN", primaryColor: "#EB172B" },
  "Tottenham Hotspur": { name: "Tottenham Hotspur", shortName: "TOT", primaryColor: "#132257" },
  "West Ham United": { name: "West Ham United", shortName: "WHU", primaryColor: "#7A263A" },
  "Wolverhampton Wanderers": { name: "Wolverhampton Wanderers", shortName: "WOL", primaryColor: "#FDB913" },
};

export const BASE_PREMIER_LEAGUE_TEAMS = ALL_PREMIER_LEAGUE_TEAMS;

export function resolveTeamName(rawName: string | null | undefined): string | null {
  if (!rawName) return null;
  const trimmed = rawName.trim();
  if (!trimmed) return null;

  if (trimmed in ALL_PREMIER_LEAGUE_TEAMS) return trimmed;
  if (trimmed in ALIAS_LOOKUP) return ALIAS_LOOKUP[trimmed];

  const lower = trimmed.toLowerCase();
  for (const key of Object.keys(ALL_PREMIER_LEAGUE_TEAMS)) {
    if (key.toLowerCase() === lower) return key;
  }
  for (const [alias, canonical] of Object.entries(ALIAS_LOOKUP)) {
    if (alias.toLowerCase() === lower) return canonical;
  }

  const stripped = trimmed.replace(/\s+(AFC|FC)$/i, "").trim();
  if (stripped in ALL_PREMIER_LEAGUE_TEAMS) return stripped;
  if (stripped in ALIAS_LOOKUP) return ALIAS_LOOKUP[stripped];
  const strippedLower = stripped.toLowerCase();
  for (const key of Object.keys(ALL_PREMIER_LEAGUE_TEAMS)) {
    if (key.toLowerCase() === strippedLower) return key;
  }
  for (const [alias, canonical] of Object.entries(ALIAS_LOOKUP)) {
    if (alias.toLowerCase() === strippedLower) return canonical;
  }

  return null;
}

export const PREMIER_LEAGUE_TEAMS: Record<string, TeamMeta> = new Proxy(ALL_PREMIER_LEAGUE_TEAMS, {
  get(target, prop: string) {
    if (typeof prop !== "string") return (target as Record<string, TeamMeta>)[prop];
    if (prop in target) return target[prop];
    const resolved = resolveTeamName(prop);
    if (resolved && resolved in target) return target[resolved];
    return undefined;
  },
  ownKeys(target) {
    return Object.keys(target);
  },
  getOwnPropertyDescriptor(target, prop) {
    return Object.getOwnPropertyDescriptor(target, prop);
  },
  has(target, prop: string) {
    if (prop in target) return true;
    const resolved = resolveTeamName(prop);
    return !!resolved && resolved in target;
  },
});

export function getTeamMeta(teamName: string): TeamMeta | undefined {
  return PREMIER_LEAGUE_TEAMS[teamName];
}

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
    away_team: "Hull City",
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

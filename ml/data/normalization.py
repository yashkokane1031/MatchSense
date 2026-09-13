"""Single source of truth for Premier League team name normalization across ingestion, models, and prediction APIs."""

# Canonical team names used by MatchSense ML models and storage:
# "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Burnley",
# "Chelsea", "Coventry", "Crystal Palace", "Everton", "Fulham", "Hull", "Ipswich",
# "Leeds", "Leicester", "Liverpool", "Luton", "Manchester City", "Manchester Utd",
# "Newcastle", "Nottingham Forest", "Sheffield Utd", "Southampton", "Tottenham",
# "West Ham", "Wolverhampton"

TEAM_CANONICAL_MAP: dict[str, str] = {
    # Manchester United
    "manchester united": "Manchester Utd",
    "man united": "Manchester Utd",
    "man utd": "Manchester Utd",
    "manchester united fc": "Manchester Utd",
    "manchester utd": "Manchester Utd",
    "manchester utd fc": "Manchester Utd",

    # Manchester City
    "manchester city": "Manchester City",
    "man city": "Manchester City",
    "manchester city fc": "Manchester City",

    # Tottenham
    "tottenham hotspur": "Tottenham",
    "tottenham hotspur fc": "Tottenham",
    "tottenham": "Tottenham",
    "spurs": "Tottenham",

    # Newcastle
    "newcastle united": "Newcastle",
    "newcastle united fc": "Newcastle",
    "newcastle": "Newcastle",

    # West Ham
    "west ham united": "West Ham",
    "west ham united fc": "West Ham",
    "west ham": "West Ham",

    # Wolverhampton
    "wolverhampton wanderers": "Wolverhampton",
    "wolverhampton wanderers fc": "Wolverhampton",
    "wolverhampton": "Wolverhampton",
    "wolves": "Wolverhampton",

    # Brighton
    "brighton & hove albion": "Brighton",
    "brighton and hove albion": "Brighton",
    "brighton & hove albion fc": "Brighton",
    "brighton": "Brighton",

    # Bournemouth
    "afc bournemouth": "Bournemouth",
    "bournemouth": "Bournemouth",

    # Nottingham Forest
    "nottingham forest": "Nottingham Forest",
    "nottingham forest fc": "Nottingham Forest",
    "nott'm forest": "Nottingham Forest",
    "nottingham": "Nottingham Forest",

    # Leicester
    "leicester city": "Leicester",
    "leicester city fc": "Leicester",
    "leicester": "Leicester",

    # Ipswich
    "ipswich town": "Ipswich",
    "ipswich town fc": "Ipswich",
    "ipswich": "Ipswich",

    # Coventry (2026-27 Promoted)
    "coventry city": "Coventry",
    "coventry city fc": "Coventry",
    "coventry": "Coventry",

    # Hull (2026-27 Promoted)
    "hull city": "Hull",
    "hull city fc": "Hull",
    "hull": "Hull",

    # Sheffield United
    "sheffield united": "Sheffield Utd",
    "sheffield united fc": "Sheffield Utd",
    "sheffield utd": "Sheffield Utd",

    # Leeds
    "leeds united": "Leeds",
    "leeds united fc": "Leeds",
    "leeds": "Leeds",

    # Luton
    "luton town": "Luton",
    "luton town fc": "Luton",
    "luton": "Luton",

    # Burnley
    "burnley fc": "Burnley",
    "burnley": "Burnley",

    # Standard FC suffixes
    "arsenal fc": "Arsenal",
    "chelsea fc": "Chelsea",
    "liverpool fc": "Liverpool",
    "everton fc": "Everton",
    "fulham fc": "Fulham",
    "southampton fc": "Southampton",
    "aston villa fc": "Aston Villa",
    "brentford fc": "Brentford",
    "crystal palace fc": "Crystal Palace",
}


def normalize_team(raw_name: str) -> str:
    """Normalize any team name variation to MatchSense canonical representation."""
    if not raw_name:
        return raw_name
    cleaned = raw_name.strip()
    # Check direct dictionary lookup (case-insensitive)
    lower = cleaned.lower()
    if lower in TEAM_CANONICAL_MAP:
        return TEAM_CANONICAL_MAP[lower]
    # Suffix stripping fallback
    stripped = cleaned.replace(" FC", "").replace("AFC ", "").strip()
    if stripped.lower() in TEAM_CANONICAL_MAP:
        return TEAM_CANONICAL_MAP[stripped.lower()]
    return stripped

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
  "Wolverhampton Wanderers": { name: "Wolverhampton Wanderers", shortName: "WOL", primaryColor: "#FDB913" },
};

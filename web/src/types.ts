export type Team = {
  team_abbr: string;
  team_name: string;
  conference: string | null;
  division: string | null;
};

export type TeamDetail = Team & {
  team_color: string | null;
  logo_url: string | null;
  season: number;
  wins: number;
  losses: number;
  ties: number;
  points_for: number;
  points_against: number;
  playoff_wins: number;
  playoff_losses: number;
};

export type Player = {
  player_id: string;
  full_name: string;
  position: string | null;
  team_abbr: string | null;
  headshot_url: string | null;
};

export type ScheduleGame = {
  game_id: string;
  season: number;
  week: number;
  game_date: string | null;
  opponent: string | null;
  is_home: boolean;
  points_for: number | null;
  points_against: number | null;
};

export type StatLine = {
  game_id: string;
  season: number;
  week: number;
  season_type: string | null;
  team: string | null;
  opponent_team: string | null;
  position: string | null;
  [key: string]: string | number | null;
};

export type SnapLine = {
  game_id: string;
  season: number;
  week: number;
  offense_snaps: number | null;
  offense_pct: number | null;
  defense_snaps: number | null;
  defense_pct: number | null;
  st_snaps: number | null;
  st_pct: number | null;
};

export type BoxLine = {
  player_id: string;
  full_name: string;
  team: string | null;
  position: string | null;
  [key: string]: string | number | null;
};

export type BoxScore = {
  game_id: string;
  season: number;
  week: number;
  game_date: string | null;
  home_team: string | null;
  away_team: string | null;
  home_score: number | null;
  away_score: number | null;
  players: BoxLine[];
};

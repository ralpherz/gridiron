"""SQL lives here, separate from the routing."""

TEAMS = """
SELECT team_abbr, team_name, conference, division
FROM   teams
ORDER  BY team_abbr
"""

PLAYERS = """
SELECT player_id, full_name, position, team_abbr
FROM   players
WHERE  (%(team)s::text IS NULL OR team_abbr = %(team)s::text)
  AND  (%(position)s::text IS NULL OR position = %(position)s::text)
  AND  (%(search)s::text IS NULL OR full_name ILIKE '%%' || %(search)s::text || '%%')
ORDER  BY full_name
LIMIT  %(limit)s OFFSET %(offset)s
"""

PLAYER_BY_ID = """
SELECT player_id, full_name, position, team_abbr, headshot_url
FROM   players
WHERE  player_id = %(player_id)s
"""
TEAM_DETAIL = """
WITH results AS (
    SELECT home_team AS team, week,
           CASE WHEN home_score > away_score THEN 1 ELSE 0 END AS win,
           CASE WHEN home_score < away_score THEN 1 ELSE 0 END AS loss,
           CASE WHEN home_score = away_score THEN 1 ELSE 0 END AS tie,
           home_score AS pf, away_score AS pa
    FROM   games
    WHERE  season = %(season)s::int AND home_score IS NOT NULL
    UNION ALL
    SELECT away_team, week,
           CASE WHEN away_score > home_score THEN 1 ELSE 0 END,
           CASE WHEN away_score < home_score THEN 1 ELSE 0 END,
           CASE WHEN away_score = home_score THEN 1 ELSE 0 END,
           away_score, home_score
    FROM   games
    WHERE  season = %(season)s::int AND away_score IS NOT NULL
)
SELECT t.team_abbr, t.team_name, t.conference, t.division,
       t.team_color, t.logo_url,
       %(season)s::int AS season,
       coalesce(sum(r.win)  FILTER (WHERE r.week <= 18), 0)::int AS wins,
       coalesce(sum(r.loss) FILTER (WHERE r.week <= 18), 0)::int AS losses,
       coalesce(sum(r.tie)  FILTER (WHERE r.week <= 18), 0)::int AS ties,
       coalesce(sum(r.pf)   FILTER (WHERE r.week <= 18), 0)::int AS points_for,
       coalesce(sum(r.pa)   FILTER (WHERE r.week <= 18), 0)::int AS points_against,
       coalesce(sum(r.win)  FILTER (WHERE r.week > 18), 0)::int  AS playoff_wins,
       coalesce(sum(r.loss) FILTER (WHERE r.week > 18), 0)::int  AS playoff_losses
FROM   teams t
LEFT   JOIN results r ON r.team = t.team_abbr
WHERE  t.team_abbr = %(team)s::text
GROUP  BY t.team_abbr, t.team_name, t.conference, t.division,
          t.team_color, t.logo_url
"""

TEAM_SCHEDULE = """
SELECT g.game_id, g.season, g.week, g.game_date,
       CASE WHEN g.home_team = %(team)s::text THEN g.away_team ELSE g.home_team END AS opponent,
       (g.home_team = %(team)s::text)                                                AS is_home,
       CASE WHEN g.home_team = %(team)s::text THEN g.home_score ELSE g.away_score END AS points_for,
       CASE WHEN g.home_team = %(team)s::text THEN g.away_score ELSE g.home_score END AS points_against
FROM   games g
WHERE  g.season = %(season)s::int
  AND  (g.home_team = %(team)s::text OR g.away_team = %(team)s::text)
ORDER  BY g.week, g.game_date
"""

TEAM_ROSTER = """
SELECT player_id, full_name, position, team_abbr, headshot_url
FROM   players
WHERE  team_abbr = %(team)s::text
ORDER  BY position, full_name
"""

PLAYER_STATS = """
SELECT game_id, season, week, season_type, team, opponent_team, position,
       completions, attempts, passing_yards, passing_tds,
       passing_interceptions, sacks_suffered, passing_epa,
       carries, rushing_yards, rushing_tds, rushing_fumbles_lost, rushing_epa,
       receptions, targets, receiving_yards, receiving_tds,
       receiving_air_yards, target_share, receiving_epa,
       def_tackles_solo, def_tackle_assists, def_tackles_for_loss,
       def_sacks, def_qb_hits, def_interceptions, def_pass_defended,
       def_tds, def_fumbles_forced,
       fg_made, fg_att, fg_long, pat_made, pat_att,
       pt_att, pt_yards, pt_net_yards, pt_inside_20,
       punt_returns, punt_return_yards, kickoff_returns,
       kickoff_return_yards, special_teams_tds,
       fantasy_points, fantasy_points_ppr
FROM   player_week_stats
WHERE  player_id = %(player_id)s::text
  AND  (%(season)s::int IS NULL OR season = %(season)s::int)
ORDER  BY season DESC, week
"""

PLAYER_SNAPS = """
SELECT game_id, season, week, team, opponent, position,
       offense_snaps, offense_pct, defense_snaps, defense_pct,
       st_snaps, st_pct
FROM   snap_counts
WHERE  player_id = %(player_id)s::text
  AND  (%(season)s::int IS NULL OR season = %(season)s::int)
ORDER  BY season DESC, week
"""

PLAYER_INJURIES = """
SELECT season, week, team, position,
       report_primary_injury, report_secondary_injury, report_status,
       practice_primary_injury, practice_secondary_injury, practice_status
FROM   injuries
WHERE  player_id = %(player_id)s::text
  AND  (%(season)s::int IS NULL OR season = %(season)s::int)
ORDER  BY season DESC, week
"""

GAME_DETAIL = """
SELECT game_id, season, week, game_date,
       home_team, away_team, home_score, away_score
FROM   games
WHERE  game_id = %(game_id)s::text
"""

GAME_BOX = """
SELECT s.player_id, p.full_name, s.team, s.position,
       s.completions, s.attempts, s.passing_yards, s.passing_tds,
       s.passing_interceptions,
       s.carries, s.rushing_yards, s.rushing_tds,
       s.receptions, s.targets, s.receiving_yards, s.receiving_tds,
       s.def_tackles_solo, s.def_sacks, s.def_interceptions,
       s.fg_made, s.fg_att, s.fantasy_points_ppr
FROM   player_week_stats s
JOIN   players p ON p.player_id = s.player_id
WHERE  s.game_id = %(game_id)s::text
ORDER  BY s.team, s.position, p.full_name
"""


HEALTH_DB = "SELECT 1 AS ok"

HEALTH_LAST_RUN = """
SELECT max(finished_at)::text AS last_run
FROM   data_runs
WHERE  status = 'success'
"""

"""SQL lives here, separate from the routing."""

TEAMS = """
SELECT team_abbr, team_name, conference, division
FROM   teams
ORDER  BY team_abbr
"""

PLAYERS = """
SELECT player_id, full_name, position, team_abbr
FROM   players
WHERE  (%(team)s IS NULL OR team_abbr = %(team)s)
  AND  (%(position)s IS NULL OR position = %(position)s)
  AND  (%(search)s IS NULL OR full_name ILIKE '%%' || %(search)s || '%%')
ORDER  BY full_name
LIMIT  %(limit)s OFFSET %(offset)s
"""

PLAYER_BY_ID = """
SELECT player_id, full_name, position, team_abbr
FROM   players
WHERE  player_id = %(player_id)s
"""
PLAYER_GAME_LOG = """
SELECT s.game_id, s.season, s.week, s.targets, s.receptions,
       s.rec_yards, s.rec_tds, s.rush_yards, s.rush_tds
FROM   player_game_stats s
WHERE  s.player_id = %(player_id)s
  AND  (%(season)s IS NULL OR s.season = %(season)s)
ORDER  BY s.season DESC, s.week
"""

GAMES = """
SELECT game_id, season, week, game_date,
       home_team, away_team, home_score, away_score
FROM   games
WHERE  season = %(season)s
  AND  (%(week)s IS NULL OR week = %(week)s)
ORDER  BY week, game_date, game_id
"""
LEADERS = """
SELECT s.player_id,
       p.full_name,
       p.position,
       p.team_abbr,
       count(*)                  AS games,
       sum(s.targets)::int       AS targets,
       sum(s.receptions)::int    AS receptions,
       sum(s.rec_yards)::int     AS rec_yards,
       sum(s.rec_tds)::int       AS rec_tds,
       sum(s.rush_yards)::int    AS rush_yards,
       sum(s.rush_tds)::int      AS rush_tds
FROM   player_game_stats s
JOIN   players p ON p.player_id = s.player_id
WHERE  s.season = %(season)s
  AND  (%(position)s IS NULL OR p.position = %(position)s)
GROUP  BY s.player_id, p.full_name, p.position, p.team_abbr
ORDER  BY {sort_column} DESC
LIMIT  %(limit)s
"""

HEALTH_DB = "SELECT 1 AS ok"

HEALTH_LAST_RUN = """
SELECT max(finished_at)::text AS last_run
FROM   data_runs
WHERE  status = 'success'
"""

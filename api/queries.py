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
SELECT player_id, full_name, position, team_abbr
FROM   players
WHERE  player_id = %(player_id)s
"""
PLAYER_GAME_LOG = """
SELECT s.game_id, s.season, s.week, s.targets, s.receptions,
       s.rec_yards, s.rec_tds, s.rush_yards, s.rush_tds
FROM   player_game_stats s
WHERE  s.player_id = %(player_id)s
  AND  (%(season)s::int IS NULL OR s.season = %(season)s::int)
ORDER  BY s.season DESC, s.week
"""

GAMES = """
SELECT game_id, season, week, game_date,
       home_team, away_team, home_score, away_score
FROM   games
WHERE  season = %(season)s::int
  AND  (%(week)s::int IS NULL OR week = %(week)s::int)
ORDER  BY week, game_date, game_id
LIMIT  %(limit)s OFFSET %(offset)s
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
WHERE  s.season = %(season)s::int
  AND  (%(position)s::text IS NULL OR p.position = %(position)s::text)
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

TEAM_DETAIL = """
WITH results AS (
    SELECT home_team AS team,
           CASE WHEN home_score > away_score THEN 1 ELSE 0 END AS win,
           CASE WHEN home_score < away_score THEN 1 ELSE 0 END AS loss,
           CASE WHEN home_score = away_score THEN 1 ELSE 0 END AS tie,
           home_score AS pf, away_score AS pa
    FROM   games
    WHERE  season = %(season)s::int AND home_score IS NOT NULL
    UNION ALL
    SELECT away_team,
           CASE WHEN away_score > home_score THEN 1 ELSE 0 END,
           CASE WHEN away_score < home_score THEN 1 ELSE 0 END,
           CASE WHEN away_score = home_score THEN 1 ELSE 0 END,
           away_score, home_score
    FROM   games
    WHERE  season = %(season)s::int AND away_score IS NOT NULL
)
SELECT t.team_abbr, t.team_name, t.conference, t.division,
       t.team_color, t.logo_url,
       %(season)s::int                       AS season,
       coalesce(sum(r.win), 0)::int          AS wins,
       coalesce(sum(r.loss), 0)::int         AS losses,
       coalesce(sum(r.tie), 0)::int          AS ties,
       coalesce(sum(r.pf), 0)::int           AS points_for,
       coalesce(sum(r.pa), 0)::int           AS points_against
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

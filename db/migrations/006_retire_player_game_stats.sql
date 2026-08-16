-- 006_retire_player_game_stats.sql
-- player_game_stats derived six columns from raw plays, covering only
-- receivers and rushers. player_week_stats carries sixty from nflverse's own
-- aggregation across every position. Keeping both would mean two versions of
-- the same numbers, and only one of them is complete.
BEGIN;

DROP TABLE player_game_stats;

COMMIT;

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { CURRENT_SEASON, get } from "../api";
import type { Player, ScheduleGame, TeamDetail } from "../types";

const POSITION_ORDER = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB", "K", "P", "LS"];
const LAST_REGULAR_WEEK = 18;

const ROUND: Record<number, string> = {
  19: "Wild Card",
  20: "Divisional",
  21: "Conference Championship",
  22: "Super Bowl",
};

type Row =
  | { kind: "game"; week: number; game: ScheduleGame }
  | { kind: "bye"; week: number };

/** Weeks 1 through 18 always exist. A week with no game is a bye. */
function regularSeasonRows(games: ScheduleGame[]): Row[] {
  const byWeek = new Map(games.map((g) => [g.week, g]));
  const rows: Row[] = [];
  for (let week = 1; week <= LAST_REGULAR_WEEK; week++) {
    const game = byWeek.get(week);
    rows.push(game ? { kind: "game", week, game } : { kind: "bye", week });
  }
  return rows;
}

export default function TeamPage() {
  const { abbr = "" } = useParams();
  const [team, setTeam] = useState<TeamDetail | null>(null);
  const [schedule, setSchedule] = useState<ScheduleGame[]>([]);
  const [roster, setRoster] = useState<Player[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    Promise.all([
      get<TeamDetail>(`/teams/${abbr}?season=${CURRENT_SEASON}`),
      get<ScheduleGame[]>(`/teams/${abbr}/schedule?season=${CURRENT_SEASON}`),
      get<Player[]>(`/teams/${abbr}/roster`),
    ])
      .then(([t, s, r]) => { setTeam(t); setSchedule(s); setRoster(r); })
      .catch((e) => setError(String(e.message ?? e)));
  }, [abbr]);

  if (error) return <p className="error">{error}</p>;
  if (!team) return <p className="loading">Loading team...</p>;

  const regular = regularSeasonRows(
    schedule.filter((g) => g.week <= LAST_REGULAR_WEEK)
  );
  const postseason = schedule.filter((g) => g.week > LAST_REGULAR_WEEK);

  const groups = POSITION_ORDER
    .map((pos) => [pos, roster.filter((p) => p.position === pos)] as const)
    .filter(([, list]) => list.length > 0);
  const other = roster.filter((p) => !POSITION_ORDER.includes(p.position ?? ""));

  const result = (g: ScheduleGame) => {
    if (g.points_for === null || g.points_against === null) return "--";
    if (g.points_for === g.points_against) return "T";
    return g.points_for > g.points_against ? "W" : "L";
  };
  const score = (g: ScheduleGame) =>
    g.points_for === null ? "--" : `${g.points_for}-${g.points_against}`;

  return (
    <div style={{ ["--accent" as string]: team.team_color ?? "#14161a" }}>
      <section className="team-head">
        {team.logo_url && (
          <img className="team-logo" src={team.logo_url} alt="" width={72} height={72} />
        )}
        <div>
          <p className="eyebrow">{team.division}</p>
          <h1 className="display team-title">{team.team_name}</h1>
          <p className="team-record">
            <strong>{team.wins}-{team.losses}{team.ties > 0 ? `-${team.ties}` : ""}</strong>
            <span className="team-record-sep">/</span>
            <span>{team.points_for} PF</span>
            <span className="team-record-sep">/</span>
            <span>{team.points_against} PA</span>
            {(team.playoff_wins > 0 || team.playoff_losses > 0) && (
              <>
                <span className="team-record-sep">/</span>
                <span>{team.playoff_wins}-{team.playoff_losses} postseason</span>
              </>
            )}
          </p>
        </div>
      </section>

      <div className="yardline" />
      <section>
        <p className="eyebrow">{CURRENT_SEASON} schedule</p>
        <table className="stats">
          <thead>
            <tr><th>Wk</th><th>Opponent</th><th>Result</th><th>Score</th></tr>
          </thead>
          <tbody>
            {regular.map((row) =>
              row.kind === "bye" ? (
                <tr key={`bye-${row.week}`} className="row-bye">
                  <td>{row.week}</td>
                  <td colSpan={3}>Bye</td>
                </tr>
              ) : (
                <tr key={row.game.game_id}>
                  <td>{row.week}</td>
                  <td>
                    <Link to={`/games/${row.game.game_id}`}>
                      {row.game.is_home ? "" : "at "}{row.game.opponent}
                    </Link>
                  </td>
                  <td>{result(row.game)}</td>
                  <td>{score(row.game)}</td>
                </tr>
              )
            )}
            {postseason.length > 0 && (
              <tr className="row-divider">
                <td colSpan={4}>Postseason</td>
              </tr>
            )}
            {postseason.map((g) => (
              <tr key={g.game_id}>
                <td>{ROUND[g.week] ? "" : g.week}</td>
                <td>
                  <Link to={`/games/${g.game_id}`}>
                    {g.is_home ? "" : "at "}{g.opponent}
                  </Link>
                  {ROUND[g.week] && <span className="round-tag">{ROUND[g.week]}</span>}
                </td>
                <td>{result(g)}</td>
                <td>{score(g)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <div className="yardline" />

      <section>
        <p className="eyebrow">Roster &middot; {roster.length} players</p>
        <div className="roster">
          {groups.map(([pos, list]) => (
            <div key={pos} className="roster-group">
              <h2 className="roster-pos">{pos}</h2>
              <ul className="roster-list">
                {list.map((p) => (
                  <li key={p.player_id}>
                    <Link to={`/players/${p.player_id}`}>{p.full_name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          {other.length > 0 && (
            <div className="roster-group">
              <h2 className="roster-pos">Other</h2>
              <ul className="roster-list">
                {other.map((p) => (
                  <li key={p.player_id}>
                    <Link to={`/players/${p.player_id}`}>{p.full_name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

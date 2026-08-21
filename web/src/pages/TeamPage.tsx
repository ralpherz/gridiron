import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { CURRENT_SEASON, get } from "../api";
import type { Player, ScheduleGame, TeamDetail } from "../types";

const POSITION_ORDER = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB", "K", "P", "LS"];

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

  const groups = POSITION_ORDER
    .map((pos) => [pos, roster.filter((p) => p.position === pos)] as const)
    .filter(([, list]) => list.length > 0);

  const other = roster.filter((p) => !POSITION_ORDER.includes(p.position ?? ""));
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
            <tr>
              <th>Wk</th><th>Opponent</th><th>Result</th><th>Score</th>
            </tr>
          </thead>
          <tbody>
            {schedule.map((g) => {
              const played = g.points_for !== null && g.points_against !== null;
              const won = played && (g.points_for as number) > (g.points_against as number);
              const tied = played && g.points_for === g.points_against;
              return (
                <tr key={g.game_id}>
                  <td>{g.week}</td>
                  <td>
                    <Link to={`/games/${g.game_id}`}>
                      {g.is_home ? "" : "at "}{g.opponent}
                    </Link>
                  </td>
                  <td>{played ? (tied ? "T" : won ? "W" : "L") : "--"}</td>
                  <td>{played ? `${g.points_for}-${g.points_against}` : "--"}</td>
                </tr>
              );
            })}
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

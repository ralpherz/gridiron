import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { get } from "../api";
import type { BoxLine, BoxScore } from "../types";

const GROUPS: { label: string; cols: { key: string; label: string }[]; test: (r: BoxLine) => boolean }[] = [
  {
    label: "Passing",
    cols: [
      { key: "completions", label: "Cmp" }, { key: "attempts", label: "Att" },
      { key: "passing_yards", label: "Yds" }, { key: "passing_tds", label: "TD" },
      { key: "passing_interceptions", label: "Int" },
    ],
    test: (r) => Number(r.attempts ?? 0) > 0,
  },
  {
    label: "Rushing",
    cols: [
      { key: "carries", label: "Car" }, { key: "rushing_yards", label: "Yds" },
      { key: "rushing_tds", label: "TD" },
    ],
    test: (r) => Number(r.carries ?? 0) > 0,
  },
  {
    label: "Receiving",
    cols: [
      { key: "targets", label: "Tgt" }, { key: "receptions", label: "Rec" },
      { key: "receiving_yards", label: "Yds" }, { key: "receiving_tds", label: "TD" },
    ],
    test: (r) => Number(r.targets ?? 0) > 0,
  },
  {
    label: "Defense",
    cols: [
      { key: "def_tackles_solo", label: "Solo" }, { key: "def_sacks", label: "Sk" },
      { key: "def_interceptions", label: "Int" },
    ],
    test: (r) => Number(r.def_tackles_solo ?? 0) > 0 || Number(r.def_sacks ?? 0) > 0,
  },
];
export default function GamePage() {
  const { gameId = "" } = useParams();
  const [box, setBox] = useState<BoxScore | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    get<BoxScore>(`/games/${gameId}`).then(setBox).catch((e) => setError(String(e.message ?? e)));
  }, [gameId]);

  if (error) return <p className="error">{error}</p>;
  if (!box) return <p className="loading">Loading box score...</p>;

  const teams = [box.away_team, box.home_team].filter(Boolean) as string[];

  return (
    <>
      <section className="game-head">
        <p className="eyebrow">
          {box.season} &middot; Week {box.week}
          {box.game_date && <> &middot; {box.game_date}</>}
        </p>
        <h1 className="display game-title">
          <Link to={`/teams/${box.away_team}`}>{box.away_team}</Link>
          <span className="game-score">{box.away_score ?? "--"}</span>
          <span className="game-at">at</span>
          <Link to={`/teams/${box.home_team}`}>{box.home_team}</Link>
          <span className="game-score">{box.home_score ?? "--"}</span>
        </h1>
      </section>

      {teams.map((team) => (
        <div key={team}>
          <div className="yardline" />
          <p className="eyebrow">{team}</p>
          {GROUPS.map((g) => {
            const rows = box.players.filter((p) => p.team === team && g.test(p));
            if (rows.length === 0) return null;
            return (
              <div key={g.label} className="box-group">
                <h3 className="box-group-label">{g.label}</h3>
                <table className="stats">
                  <thead>
                    <tr>
                      <th>Player</th>
                      {g.cols.map((c) => <th key={c.key}>{c.label}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((p) => (
                      <tr key={p.player_id}>
                        <td><Link to={`/players/${p.player_id}`}>{p.full_name}</Link></td>
                        {g.cols.map((c) => <td key={c.key}>{p[c.key] ?? "--"}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })}
        </div>
      ))}
    </>
  );
}

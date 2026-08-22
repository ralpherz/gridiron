import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { CURRENT_SEASON, get } from "../api";
import type { Player, ScheduleGame, SnapLine, StatLine } from "../types";

type Col = { key: string; label: string };

const LAST_REGULAR_WEEK = 18;
const ROUND: Record<number, string> = {
  19: "Wild Card", 20: "Divisional", 21: "Conf. Champ.", 22: "Super Bowl",
};

const PASSING: Col[] = [
  { key: "completions", label: "Cmp" }, { key: "attempts", label: "Att" },
  { key: "passing_yards", label: "Yds" }, { key: "passing_tds", label: "TD" },
  { key: "passing_interceptions", label: "Int" }, { key: "sacks_suffered", label: "Sk" },
];
const RUSHING: Col[] = [
  { key: "carries", label: "Car" }, { key: "rushing_yards", label: "Yds" },
  { key: "rushing_tds", label: "TD" },
];
const RECEIVING: Col[] = [
  { key: "targets", label: "Tgt" }, { key: "receptions", label: "Rec" },
  { key: "receiving_yards", label: "Yds" }, { key: "receiving_tds", label: "TD" },
];
const DEFENSE: Col[] = [
  { key: "def_tackles_solo", label: "Solo" }, { key: "def_tackle_assists", label: "Ast" },
  { key: "def_sacks", label: "Sk" }, { key: "def_qb_hits", label: "QBH" },
  { key: "def_interceptions", label: "Int" }, { key: "def_pass_defended", label: "PD" },
];
const KICKING: Col[] = [
  { key: "fg_made", label: "FGM" }, { key: "fg_att", label: "FGA" },
  { key: "fg_long", label: "Lng" }, { key: "pat_made", label: "XPM" },
];
const PUNTING: Col[] = [
  { key: "pt_att", label: "Punts" }, { key: "pt_yards", label: "Yds" },
  { key: "pt_net_yards", label: "Net" }, { key: "pt_inside_20", label: "I20" },
];

const BY_POSITION: Record<string, Col[]> = {
  QB: [...PASSING, ...RUSHING],
  RB: [...RUSHING, ...RECEIVING],
  FB: [...RUSHING, ...RECEIVING],
  WR: [...RECEIVING, ...RUSHING],
  TE: RECEIVING,
  K: KICKING,
  P: PUNTING,
};

function columnsFor(position: string | null, rows: StatLine[]): Col[] {
  const preset = position ? BY_POSITION[position] : undefined;
  if (preset) return preset;
  const total = (cols: Col[]) =>
    cols.reduce((sum, c) => sum + rows.reduce((s, r) => s + Number(r[c.key] ?? 0), 0), 0);
  if (total(DEFENSE) > 0) return DEFENSE;
  if (total(RECEIVING) > 0) return [...RECEIVING, ...RUSHING];
  if (total(RUSHING) > 0) return RUSHING;
  return DEFENSE;
}

type LogRow =
  | { kind: "played"; week: number; stat: StatLine }
  | { kind: "bye"; week: number }
  | { kind: "dnp"; week: number; opponent: string | null };

/**
 * A gap in a player's log means one of two different things. If the team had
 * no game that week it is a bye; if the team played and the player has no
 * line, he did not play. Only the team schedule can tell them apart.
 */
function buildLog(stats: StatLine[], schedule: ScheduleGame[]): LogRow[] {
  const played = new Map(stats.map((s) => [s.week, s]));
  const teamWeeks = new Map(schedule.map((g) => [g.week, g]));
  const rows: LogRow[] = [];

  for (let week = 1; week <= LAST_REGULAR_WEEK; week++) {
    const stat = played.get(week);
    if (stat) { rows.push({ kind: "played", week, stat }); continue; }
    const game = teamWeeks.get(week);
    rows.push(
      game
        ? { kind: "dnp", week, opponent: game.opponent }
        : { kind: "bye", week }
    );
  }

  for (const s of stats.filter((s) => s.week > LAST_REGULAR_WEEK)) {
    rows.push({ kind: "played", week: s.week, stat: s });
  }
  return rows;
}

export default function PlayerPage() {
  const { playerId = "" } = useParams();
  const [player, setPlayer] = useState<Player | null>(null);
  const [rows, setRows] = useState<StatLine[]>([]);
  const [snaps, setSnaps] = useState<SnapLine[]>([]);
  const [schedule, setSchedule] = useState<ScheduleGame[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    Promise.all([
      get<Player>(`/players/${playerId}`),
      get<StatLine[]>(`/players/${playerId}/stats?season=${CURRENT_SEASON}`),
      get<SnapLine[]>(`/players/${playerId}/snaps?season=${CURRENT_SEASON}`),
    ])
      .then(([p, s, sn]) => {
        setPlayer(p);
        setRows(s);
        setSnaps(sn);
        if (p.team_abbr) {
          get<ScheduleGame[]>(`/teams/${p.team_abbr}/schedule?season=${CURRENT_SEASON}`)
            .then(setSchedule)
            .catch(() => setSchedule([]));
        }
      })
      .catch((e) => setError(String(e.message ?? e)));
  }, [playerId]);

  if (error) return <p className="error">{error}</p>;
  if (!player) return <p className="loading">Loading player...</p>;

  const cols = columnsFor(player.position, rows);
  const totals = cols.map((c) => rows.reduce((s, r) => s + Number(r[c.key] ?? 0), 0));
  const snapByWeek = new Map(snaps.map((s) => [s.week, s]));
  const peak = Math.max(1, ...rows.map((r) => Number(r.fantasy_points_ppr ?? 0)));
  const log = buildLog(rows, schedule);

  return (
    <>
      <section className="player-head">
        <img
          className="player-photo"
          src={player.headshot_url ?? "/player-silhouette.svg"}
          onError={(e) => { e.currentTarget.src = "/player-silhouette.svg"; }}
          alt=""
          width={96}
          height={96}
        />
        <div>
          <p className="eyebrow">
            {player.position ?? "--"}
            {player.team_abbr && (
              <> &middot; <Link to={`/teams/${player.team_abbr}`}>{player.team_abbr}</Link></>
            )}
          </p>
          <h1 className="display player-title">{player.full_name}</h1>
        </div>
      </section>

      {rows.length > 0 && (
        <section className="strip-section">
          <p className="eyebrow">Season shape &middot; scoring by week</p>
          <div className="strip">
            {rows.map((r) => {
              const v = Number(r.fantasy_points_ppr ?? 0);
              const h = Math.max(2, Math.round((v / peak) * 46));
              return (
                <div key={r.game_id} className="strip-cell" title={`Week ${r.week}: ${v.toFixed(1)}`}>
                  <div className="strip-bar" style={{ height: `${h}px` }} />
                  <span className="strip-week">{r.week}</span>
                </div>
              );
            })}
          </div>
        </section>
      )}

      <div className="yardline" />
      <section>
        <p className="eyebrow">{CURRENT_SEASON} game log</p>
        {rows.length === 0 ? (
          <p className="loading">No games recorded for this season.</p>
        ) : (
          <table className="stats">
            <thead>
              <tr>
                <th>Wk</th><th>Opp</th>
                {cols.map((c) => <th key={c.key}>{c.label}</th>)}
                <th>Snap%</th>
              </tr>
            </thead>
            <tbody>
              {log.map((row) => {
                if (row.kind === "bye") {
                  return (
                    <tr key={`bye-${row.week}`} className="row-bye">
                      <td>{row.week}</td>
                      <td colSpan={cols.length + 2}>Bye</td>
                    </tr>
                  );
                }
                if (row.kind === "dnp") {
                  return (
                    <tr key={`dnp-${row.week}`} className="row-bye">
                      <td>{row.week}</td>
                      <td>{row.opponent}</td>
                      <td colSpan={cols.length + 1}>Did not play</td>
                    </tr>
                  );
                }
                const r = row.stat;
                const sn = snapByWeek.get(r.week);
                const pct = sn?.offense_pct ?? sn?.defense_pct ?? sn?.st_pct ?? null;
                return (
                  <tr key={r.game_id}>
                    <td>
                      {r.week}
                      {ROUND[r.week] && <span className="round-tag">{ROUND[r.week]}</span>}
                    </td>
                    <td><Link to={`/games/${r.game_id}`}>{r.opponent_team}</Link></td>
                    {cols.map((c) => <td key={c.key}>{r[c.key] ?? "--"}</td>)}
                    <td>{pct !== null ? `${Math.round(Number(pct) * 100)}%` : "--"}</td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={2}>Season</td>
                {totals.map((t, i) => <td key={cols[i].key}>{Math.round(t * 10) / 10}</td>)}
                <td>--</td>
              </tr>
            </tfoot>
          </table>
        )}
      </section>
    </>
  );
}

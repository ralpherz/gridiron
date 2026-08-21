import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { get } from "../api";
import type { Player, Team } from "../types";

const DIVISION_ORDER = [
  "AFC East", "AFC North", "AFC South", "AFC West",
  "NFC East", "NFC North", "NFC South", "NFC West",
];

export default function Home() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Player[]>([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    get<Team[]>("/teams").then(setTeams).catch(() => setTeams([]));
  }, []);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    setSearching(true);
    const timer = setTimeout(() => {
      get<Player[]>(`/players?search=${encodeURIComponent(query)}&limit=8`)
        .then(setResults)
        .catch(() => setResults([]))
        .finally(() => setSearching(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [query]);

  const byDivision = useMemo(() => {
    const map = new Map<string, Team[]>();
    for (const t of teams) {
      const key = t.division ?? "Other";
      map.set(key, [...(map.get(key) ?? []), t]);
    }
    return map;
  }, [teams]);
  return (
    <>
      <section className="hero">
        <p className="eyebrow">Every player. Every week. Every team.</p>
        <h1 className="display hero-title">
          The numbers behind<br />the season.
        </h1>
        <p className="hero-copy">
          Play-by-play, rosters, snap counts, and injury reports are pulled from
          public NFL data on a schedule, loaded into Postgres, and served here.
          Nothing is scraped live at page load and nothing is estimated. When a
          game finishes, the next run picks it up.
        </p>
      </section>

      <section className="search">
        <label className="eyebrow" htmlFor="q">Find a player</label>
        <input
          id="q"
          className="search-input"
          type="search"
          placeholder="Start typing a name"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoComplete="off"
        />
        {query.trim().length >= 2 && (
          <div className="search-results">
            {searching && results.length === 0 && (
              <p className="loading">Searching...</p>
            )}
            {!searching && results.length === 0 && (
              <p className="loading">No player by that name.</p>
            )}
            {results.map((p) => (
              <Link key={p.player_id} to={`/players/${p.player_id}`} className="search-hit">
                <span className="search-hit-name">{p.full_name}</span>
                <span className="search-hit-meta">
                  {p.position ?? "--"} &middot; {p.team_abbr ?? "Free agent"}
                </span>
              </Link>
            ))}
          </div>
        )}
      </section>

      <div className="yardline" />
      <section>
        <p className="eyebrow">Browse by team</p>
        <div className="divisions">
          {DIVISION_ORDER.filter((d) => byDivision.has(d)).map((division) => (
            <div key={division} className="division">
              <h2 className="division-name">{division}</h2>
              <ul className="team-list">
                {(byDivision.get(division) ?? []).map((t) => (
                  <li key={t.team_abbr}>
                    <Link to={`/teams/${t.team_abbr}`} className="team-row">
                      <span className="team-abbr">{t.team_abbr}</span>
                      <span className="team-name">{t.team_name}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

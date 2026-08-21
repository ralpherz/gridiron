import { Link, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import TeamPage from "./pages/TeamPage";
import PlayerPage from "./pages/PlayerPage";
import GamePage from "./pages/GamePage";

export default function App() {
  return (
    <>
      <header className="masthead">
        <div className="wrap masthead-inner">
          <Link to="/" className="masthead-mark">
            <span className="masthead-word">GRIDIRON</span>
            <span className="masthead-sub">NFL statistics</span>
          </Link>
        </div>
      </header>

      <main className="wrap">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/teams/:abbr" element={<TeamPage />} />
          <Route path="/players/:playerId" element={<PlayerPage />} />
          <Route path="/games/:gameId" element={<GamePage />} />
        </Routes>
      </main>

      <footer className="footer">
        <div className="wrap">
          <p className="eyebrow">
            Data from nflverse. Ingested on a schedule, not scraped live.
          </p>
        </div>
      </footer>
    </>
  );
}

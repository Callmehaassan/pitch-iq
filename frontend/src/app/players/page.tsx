"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Player {
  player_id: number;
  name: string;
  nationality: string;
  primary_position: string;
}

const LEAGUES = [
  { id: 0, name: "All Leagues" },
  { id: 1, name: "Premier League" },
  { id: 2, name: "La Liga" },
  { id: 3, name: "Bundesliga" },
  { id: 4, name: "Serie A" },
  { id: 5, name: "Ligue 1" },
];

export default function PlayersPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedLeague, setSelectedLeague] = useState(0);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const LIMIT = 50;

  const loadPlayers = useCallback(
    (
      newSearch: string,
      leagueId: number,
      newSkip: number,
      append: boolean
    ) => {
      setLoading(true);

      api.getPlayers(newSkip, LIMIT, newSearch, leagueId)
        .then((data) => {
          if (append) {
            setPlayers((prev) => [...prev, ...data]);
          } else {
            setPlayers(data);
          }

          setHasMore(data.length === LIMIT);
        })
        .catch(() => {
          setPlayers([]);
          setHasMore(false);
        })
        .finally(() => setLoading(false));
    },
    []
  );

  useEffect(() => {
    const timer = setTimeout(() => {
      setSkip(0);
      loadPlayers(search, selectedLeague, 0, false);
    }, 300);

    return () => clearTimeout(timer);
  }, [search, selectedLeague, loadPlayers]);

  function loadMore() {
    const newSkip = skip + LIMIT;
    setSkip(newSkip);
    loadPlayers(search, selectedLeague, newSkip, true);
  }

  const posColor = (pos: string) => {
    if (!pos)
      return "bg-[#0a1226] text-slate-400 border border-blue-900/30";

    if (pos.includes("FW"))
      return "bg-red-950/50 text-red-400 border border-red-900/50";

    if (pos.includes("MF"))
      return "bg-blue-950/50 text-blue-400 border border-blue-800/50";

    if (pos.includes("DF"))
      return "bg-yellow-950/50 text-yellow-400 border border-yellow-900/50";

    if (pos.includes("GK"))
      return "bg-purple-950/50 text-purple-400 border border-purple-900/50";

    return "bg-[#0a1226] text-slate-400 border border-blue-900/30";
  };

  return (
    <main className="min-h-screen text-slate-100">
      {/* Hero */}
      <div className="relative border-b border-blue-900/40 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_-20%,_#1e3a8a_0%,_transparent_60%)] opacity-70" />

        <div className="relative max-w-6xl mx-auto px-8 pt-14 pb-10">
          <Link
            href="/"
            className="text-slate-500 hover:text-blue-400 transition-colors text-xs font-bold uppercase tracking-widest mb-6 block"
          >
            &larr; Back to Dashboard
          </Link>

          <h1 className="text-4xl md:text-5xl font-black text-white mb-2 uppercase tracking-tight">
            Player{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">
              Stats
            </span>
          </h1>

          <p className="text-slate-400">
            Search players across all leagues.
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-10">
        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search any player by name..."
            className="w-full bg-[#070c1a] border border-blue-900/40 focus:border-blue-500 text-white px-4 py-3 outline-none transition-colors placeholder:text-slate-600"
          />
        </div>

        {/* League Filters */}
        <div className="flex gap-2 mb-10 flex-wrap">
          {LEAGUES.map((league) => (
            <button
              key={league.id}
              onClick={() => setSelectedLeague(league.id)}
              className={
                "px-4 py-2 text-xs font-bold uppercase tracking-wide border transition-all " +
                (selectedLeague === league.id
                  ? "bg-blue-600 text-white border-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.4)]"
                  : "bg-[#070c1a] text-slate-400 border-blue-900/40 hover:border-blue-500/50 hover:text-white")
              }
            >
              {league.name}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && players.length === 0 && (
          <div className="text-center text-slate-500 animate-pulse py-12 text-sm">
            Loading players...
          </div>
        )}

        {/* Players Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {players.map((player) => (
            <Link
              key={player.player_id}
              href={`/players/${player.player_id}`}
              className="group relative bg-[#070c1a] border border-blue-900/40 p-5 hover:border-blue-500/60 hover:-translate-y-0.5 transition-all duration-200 block overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-20 h-20 bg-blue-600/10 blur-2xl group-hover:bg-blue-600/25 transition-all" />

              <div className="relative flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-slate-100 text-lg">
                    {player.name}
                  </h3>

                  <p className="text-slate-500 text-sm mt-0.5">
                    {player.nationality || "Unknown"}
                  </p>
                </div>

                <span
                  className={
                    "text-[11px] px-2.5 py-1 font-bold uppercase tracking-wide " +
                    posColor(player.primary_position)
                  }
                >
                  {player.primary_position || "N/A"}
                </span>
              </div>
            </Link>
          ))}
        </div>

        {/* Empty State */}
        {players.length === 0 && !loading && (
          <div className="text-center py-12 text-slate-500 font-medium text-sm">
            No players found.
          </div>
        )}

        {/* Load More */}
        {hasMore && (
          <div className="mt-10 text-center">
            <button
              onClick={loadMore}
              disabled={loading}
              className="bg-[#070c1a] hover:bg-[#0a1226] disabled:opacity-50 border border-blue-900/40 text-slate-200 px-6 py-3 text-xs font-bold uppercase tracking-widest hover:border-blue-500/50 transition-all"
            >
              {loading ? "Loading..." : "Load More Players"}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
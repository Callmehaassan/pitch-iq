"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface League {
  league_id: number;
  name: string;
  country: string;
  tier: number;
}

export default function Home() {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getLeagues()
      .then(setLeagues)
      .catch(() => setError("Could not connect to backend"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen text-slate-100">
      {/* Hero with real image */}
      <div className="relative border-b border-blue-900/40 overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('/images/hero-bg.jpg')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#05070f]/70 via-[#05070f]/85 to-[#05070f]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_-20%,_#1e3a8a_0%,_transparent_60%)] opacity-60" />
        <div className="relative max-w-6xl mx-auto px-8 pt-24 pb-20">
          <p className="text-blue-400 text-xs font-bold tracking-[0.3em] uppercase mb-4">
            Football Intelligence Platform
          </p>
          <h1 className="text-5xl md:text-7xl font-black tracking-tight mb-4 uppercase leading-[0.95] drop-shadow-[0_4px_20px_rgba(0,0,0,0.6)]">
            Pitch <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">IQ</span>
          </h1>
          <p className="text-slate-300 text-lg max-w-xl drop-shadow-[0_2px_10px_rgba(0,0,0,0.6)]">
            Multi-League Football Performance Prediction System
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-blue-900/30 border border-blue-900/40 mb-12">
          <div className="bg-[#070c1a] p-6 hover:bg-[#0a1226] transition-colors">
            <p className="text-slate-500 text-[11px] font-bold uppercase tracking-widest mb-2">Leagues Tracked</p>
            <p className="text-4xl font-black text-blue-400">5</p>
            <p className="text-slate-600 text-xs mt-2">EPL, La Liga, Bundesliga, Serie A, Ligue 1</p>
          </div>
          <div className="bg-[#070c1a] p-6 hover:bg-[#0a1226] transition-colors">
            <p className="text-slate-500 text-[11px] font-bold uppercase tracking-widest mb-2">Seasons of Data</p>
            <p className="text-4xl font-black text-blue-400">6</p>
            <p className="text-slate-600 text-xs mt-2">Covering 6 seasons of historical data</p>
          </div>
          <div className="bg-[#070c1a] p-6 hover:bg-[#0a1226] transition-colors">
            <p className="text-slate-500 text-[11px] font-bold uppercase tracking-widest mb-2">AI Model</p>
            <p className="text-4xl font-black text-blue-400">Groq</p>
            <p className="text-slate-600 text-xs mt-2">llama-3.3-70b-versatile</p>
          </div>
        </div>

        <div className="bg-[#070c1a] border border-blue-900/40 mb-12">
          <div className="px-6 py-4 border-b border-blue-900/40 flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-widest text-white">Leagues</h2>
            <span className="w-6 h-0.5 bg-blue-500" />
          </div>
          <div className="p-6">
            {loading && <p className="text-slate-500 animate-pulse text-sm">Loading...</p>}
            {error && (
              <div className="bg-red-950/40 border border-red-900/50 p-4">
                <p className="text-red-400 font-semibold text-sm">{error}</p>
                <p className="text-slate-500 text-xs mt-1">Make sure the backend is running on port 8000</p>
              </div>
            )}
            {!loading && !error && leagues.length === 0 && (
              <div className="bg-yellow-950/30 border border-yellow-900/50 p-4">
                <p className="text-yellow-400 font-semibold text-sm">No leagues in database yet.</p>
                <p className="text-slate-500 text-xs mt-1">Run the data pipeline to populate leagues.</p>
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {leagues.map((league) => (
                <div
                  key={league.league_id}
                  className="bg-[#0a1226] border border-blue-900/30 p-4 hover:border-blue-500/50 hover:bg-[#0d1730] transition-all duration-200"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-bold text-slate-100 text-sm">{league.name}</p>
                      <p className="text-slate-500 text-xs mt-0.5">{league.country}</p>
                    </div>
                    <span className="bg-blue-950/60 text-blue-400 text-[11px] px-2.5 py-1 font-bold border border-blue-800/40 uppercase tracking-wide">
                      Tier {league.tier}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a href="/league" className="group relative bg-[#070c1a] border border-blue-900/40 p-6 hover:border-blue-500/60 transition-all duration-200 block overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-600/10 blur-2xl group-hover:bg-blue-600/25 transition-all" />
            <h3 className="text-base font-bold text-white mb-2 uppercase tracking-wide relative">League Predictions</h3>
            <p className="text-slate-500 text-sm relative">View standings and 2026/27 title winner predictions from historical league data.</p>
          </a>
          <a href="/ucl" className="group relative bg-[#070c1a] border border-blue-900/40 p-6 hover:border-blue-500/60 transition-all duration-200 block overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-600/10 blur-2xl group-hover:bg-blue-600/25 transition-all" />
            <h3 className="text-base font-bold text-white mb-2 uppercase tracking-wide relative">UCL 2026/27 Predictions</h3>
            <p className="text-slate-500 text-sm relative">Champions League winner and bracket simulation based on domestic league performance.</p>
          </a>
          <a href="/players" className="group relative bg-[#070c1a] border border-blue-900/40 p-6 hover:border-blue-500/60 transition-all duration-200 block overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-600/10 blur-2xl group-hover:bg-blue-600/25 transition-all" />
            <h3 className="text-base font-bold text-white mb-2 uppercase tracking-wide relative">Player Stats</h3>
            <p className="text-slate-500 text-sm relative">Search players, view historical stats and performance predictions.</p>
          </a>
          <a href="/scout" className="group relative bg-[#070c1a] border border-blue-900/40 p-6 hover:border-blue-500/60 transition-all duration-200 block overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-600/10 blur-2xl group-hover:bg-blue-600/25 transition-all" />
            <h3 className="text-base font-bold text-white mb-2 uppercase tracking-wide relative">Scout Finder</h3>
            <p className="text-slate-500 text-sm relative">Ask the AI data agent anything about players and teams.</p>
          </a>
          <a href="/transfer" className="group relative bg-[#070c1a] border border-blue-900/40 p-6 hover:border-blue-500/60 transition-all duration-200 block overflow-hidden md:col-span-2">
            <div className="absolute top-0 right-0 w-24 h-24 bg-blue-600/10 blur-2xl group-hover:bg-blue-600/25 transition-all" />
            <h3 className="text-base font-bold text-white mb-2 uppercase tracking-wide relative">Transfer Simulator</h3>
            <p className="text-slate-500 text-sm relative">Simulate transfers and see predicted impact on both clubs.</p>
          </a>
        </div>
      </div>
    </main>
  );
}

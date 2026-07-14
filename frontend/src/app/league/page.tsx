"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface League {
  league_id: number;
  name: string;
  country: string;
}

interface Standing {
  id: number;
  club_id: number;
  club_name: string;
  position: number;
  points: number;
  xG: number;
  xGA: number;
  possession: number;
  wins: number;
  draws: number;
  losses: number;
  matches_played: number;
}

const SEASONS = [
  { id: 6, label: "2025/26" },
  { id: 1, label: "2024/25" },
  { id: 2, label: "2023/24" },
  { id: 3, label: "2022/23" },
  { id: 5, label: "2021/22" },
  { id: 4, label: "2020/21" },
];

export default function LeaguePage() {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [selectedLeague, setSelectedLeague] = useState<number | null>(null);
  const [selectedSeason, setSelectedSeason] = useState(6);
  const [standings, setStandings] = useState<Standing[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getLeagues().then((data) => {
      setLeagues(data);
      if (data.length > 0) setSelectedLeague(data[0].league_id);
    });
  }, []);

  useEffect(() => {
    if (!selectedLeague) return;
    setLoading(true);
    api.getLeagueStandings(selectedLeague, selectedSeason)
      .then(setStandings)
      .catch(() => setStandings([]))
      .finally(() => setLoading(false));
  }, [selectedLeague, selectedSeason]);

  const selectedLeagueName = leagues.find(l => l.league_id === selectedLeague)?.name || "";

  return (
    <main className="min-h-screen text-slate-100">
      <div className="relative border-b border-blue-900/40 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_-20%,_#1e3a8a_0%,_transparent_60%)] opacity-70" />
        <div className="relative max-w-6xl mx-auto px-8 pt-14 pb-10">
          <a href="/" className="text-slate-500 hover:text-blue-400 transition-colors text-xs font-bold uppercase tracking-widest mb-6 block">
            &larr; Back to Dashboard
          </a>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-2 uppercase tracking-tight">
            League <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">Standings</span>
          </h1>
          <p className="text-slate-400">Historical standings across all seasons.</p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-10">
        <div className="flex gap-2 mb-4 flex-wrap">
          {leagues.map((league) => (
            <button
              key={league.league_id}
              onClick={() => setSelectedLeague(league.league_id)}
              className={"px-4 py-2 text-xs font-bold uppercase tracking-wide border transition-all " +
                (selectedLeague === league.league_id
                  ? "bg-blue-600 text-white border-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.4)]"
                  : "bg-[#070c1a] text-slate-400 border-blue-900/40 hover:border-blue-500/50 hover:text-white")}
            >
              {league.name}
            </button>
          ))}
        </div>

        <div className="flex gap-2 mb-8 flex-wrap">
          {SEASONS.map((season) => (
            <button
              key={season.id}
              onClick={() => setSelectedSeason(season.id)}
              className={"px-3 py-1.5 text-[11px] font-bold uppercase tracking-wide border transition-all " +
                (selectedSeason === season.id
                  ? "bg-indigo-600 text-white border-indigo-500"
                  : "bg-[#070c1a] text-slate-500 border-blue-900/30 hover:border-indigo-500/50 hover:text-white")}
            >
              {season.label}
            </button>
          ))}
        </div>

        <div className="bg-[#070c1a] border border-blue-900/40 overflow-hidden">
          <div className="p-6 border-b border-blue-900/40 flex items-center justify-between bg-[#0a1226]">
            <h2 className="text-lg font-bold text-white uppercase tracking-wide">{selectedLeagueName}</h2>
            <span className="text-blue-400 text-xs font-bold uppercase tracking-widest">{SEASONS.find(s => s.id === selectedSeason)?.label}</span>
          </div>

          {loading && <div className="p-8 text-center text-slate-500 animate-pulse text-sm">Loading standings...</div>}

          {!loading && standings.length === 0 && (
            <div className="p-8 text-center">
              <p className="text-slate-500 text-sm">No standings data for this season.</p>
            </div>
          )}

          {!loading && standings.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[#0a1226] text-slate-500 uppercase text-[11px] tracking-widest border-b border-blue-900/40">
                    <th className="text-left p-4 w-8">#</th>
                    <th className="text-left p-4">Club</th>
                    <th className="text-center p-4">MP</th>
                    <th className="text-center p-4">W</th>
                    <th className="text-center p-4">D</th>
                    <th className="text-center p-4">L</th>
                    <th className="text-center p-4">xG</th>
                    <th className="text-center p-4">xGA</th>
                    <th className="text-center p-4 font-bold text-slate-200">Pts</th>
                  </tr>
                </thead>
                <tbody>
                  {standings.map((s, i) => (
                    <tr
                      key={s.id}
                      className={"border-b border-blue-900/20 hover:bg-blue-950/30 transition-colors " +
                        (i % 2 === 1 ? "bg-[#080d1c] " : "") +
                        (i < 4 ? "border-l-2 border-l-blue-500" :
                        i >= standings.length - 3 ? "border-l-2 border-l-red-500" : "")}
                    >
                      <td className="p-4 text-slate-500 font-medium">{s.position || i + 1}</td>
                      <td className="p-4 font-bold text-slate-100">{s.club_name}</td>
                      <td className="p-4 text-center text-slate-400">{s.matches_played || "-"}</td>
                      <td className="p-4 text-center text-slate-400">{s.wins || "-"}</td>
                      <td className="p-4 text-center text-slate-400">{s.draws || "-"}</td>
                      <td className="p-4 text-center text-slate-400">{s.losses || "-"}</td>
                      <td className="p-4 text-center text-slate-400">{s.xG ? s.xG.toFixed(1) : "-"}</td>
                      <td className="p-4 text-center text-slate-400">{s.xGA ? s.xGA.toFixed(1) : "-"}</td>
                      <td className="p-4 text-center font-black text-blue-400 text-base">{s.points || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="mt-4 flex gap-6 text-xs text-slate-500">
          <span className="flex items-center gap-2"><span className="w-3 h-1 bg-blue-500 rounded"></span>Champions League</span>
          <span className="flex items-center gap-2"><span className="w-3 h-1 bg-red-500 rounded"></span>Relegation Zone</span>
        </div>
      </div>
    </main>
  );
}
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Prediction {
  club_id: number;
  club_name: string;
  predicted_points: number;
  last_season_points: number;
  trend: number;
  seasons_used: number;
}

interface LeaguePrediction {
  league_id: number;
  season: string;
  predictions: Prediction[];
}

const LEAGUES = [
  { id: 1, name: "Premier League" },
  { id: 2, name: "La Liga" },
  { id: 3, name: "Bundesliga" },
  { id: 4, name: "Serie A" },
  { id: 5, name: "Ligue 1" },
];

export default function PredictionsPage() {
  const [selectedLeague, setSelectedLeague] = useState(1);
  const [data, setData] = useState<LeaguePrediction | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    setData(null);

    fetch(`http://localhost:8000/predict/next-season/${selectedLeague}`)
      .then((res) => res.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [selectedLeague]);

  const trendColor = (trend: number) => {
    if (trend > 5) return "text-green-400";
    if (trend < -5) return "text-red-400";
    return "text-yellow-400";
  };

  const posColor = (pos: number, total: number) => {
    if (pos === 1) return "bg-blue-900/20 border-l-2 border-l-blue-500";
    if (pos <= 4) return "border-l-2 border-l-blue-500";
    if (pos <= 6) return "border-l-2 border-l-indigo-500";
    if (pos >= total - 2) return "border-l-2 border-l-red-500";
    return "";
  };

  return (
    <main className="min-h-screen text-slate-100">
      {/* Header */}
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
            2026/27{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">
              Predictions
            </span>
          </h1>

          <p className="text-slate-400">
            XGBoost predictions trained on 6 seasons of data.
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-10">
        {/* League Buttons */}
        <div className="flex gap-2 mb-8 flex-wrap">
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
        {loading && (
          <div className="text-center text-slate-500 animate-pulse py-12 text-sm">
            Running predictions...
          </div>
        )}

        {/* Results */}
        {data?.predictions && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="relative bg-gradient-to-br from-blue-900/50 to-indigo-950/50 border border-blue-700/50 p-5 shadow-[0_0_20px_rgba(59,130,246,0.15)] overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/20 blur-2xl" />

                <div className="relative">
                  <p className="text-blue-300 text-[11px] uppercase tracking-widest font-bold mb-2">
                    Predicted Champion
                  </p>

                  <p className="text-2xl font-black text-white">
                    {data.predictions[0]?.club_name}
                  </p>

                  <p className="text-blue-400 font-black text-lg mt-2">
                    {data.predictions[0]?.predicted_points} pts
                  </p>
                </div>
              </div>

              <div className="bg-[#070c1a] p-5 border border-blue-900/40">
                <p className="text-slate-500 text-[11px] uppercase tracking-widest font-bold mb-2">
                  Season
                </p>

                <p className="text-xl font-black text-white">2026/27</p>

                <p className="text-slate-600 text-sm mt-1">
                  Based on {data.predictions[0]?.seasons_used} seasons
                </p>
              </div>

              <div className="bg-[#070c1a] p-5 border border-blue-900/40">
                <p className="text-slate-500 text-[11px] uppercase tracking-widest font-bold mb-2">
                  Teams Predicted
                </p>

                <p className="text-xl font-black text-white">
                  {data.predictions.length}
                </p>

                <p className="text-slate-600 text-sm mt-1">
                  XGBoost Model
                </p>
              </div>
            </div>

            <div className="bg-[#070c1a] border border-blue-900/40 overflow-hidden">
              <div className="p-6 border-b border-blue-900/40 bg-[#0a1226]">
                <h2 className="text-lg font-bold text-white uppercase tracking-wide">
                  Predicted Standings 2026/27
                </h2>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="uppercase text-[11px] tracking-widest text-slate-500 bg-[#0a1226] border-b border-blue-900/40">
                      <th className="text-left p-4">#</th>
                      <th className="text-left p-4">Club</th>
                      <th className="text-center p-4">Pred Pts</th>
                      <th className="text-center p-4">Last Season</th>
                      <th className="text-center p-4">Trend</th>
                      <th className="text-center p-4">Seasons</th>
                    </tr>
                  </thead>

                  <tbody>
                    {data.predictions.map((team, index) => (
                      <tr
                        key={team.club_id}
                        className={
                          "border-b border-blue-900/20 hover:bg-blue-950/30 transition-colors " +
                          posColor(index + 1, data.predictions.length)
                        }
                      >
                        <td className="p-4 text-slate-500">{index + 1}</td>

                        <td className="p-4 font-bold text-white">
                          {team.club_name}
                        </td>

                        <td className="p-4 text-center text-blue-400 font-black text-base">
                          {team.predicted_points}
                        </td>

                        <td className="p-4 text-center text-slate-400">
                          {team.last_season_points}
                        </td>

                        <td
                          className={
                            "p-4 text-center font-bold " +
                            trendColor(team.trend)
                          }
                        >
                          {team.trend > 0
                            ? `▲ +${team.trend}`
                            : team.trend < 0
                            ? `▼ ${team.trend}`
                            : "— 0"}
                        </td>

                        <td className="p-4 text-center text-slate-500">
                          {team.seasons_used}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="p-4 flex gap-6 text-xs text-slate-500 border-t border-blue-900/40 bg-[#0a1226]">
                <span className="flex items-center gap-2">
                  <span className="w-3 h-1 bg-blue-500 rounded"></span>
                  Champions League
                </span>

                <span className="flex items-center gap-2">
                  <span className="w-3 h-1 bg-indigo-500 rounded"></span>
                  Europa League
                </span>

                <span className="flex items-center gap-2">
                  <span className="w-3 h-1 bg-red-500 rounded"></span>
                  Relegation
                </span>
              </div>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";

interface Player {
  player_id: number;
  name: string;
  nationality: string;
  primary_position: string;
}

interface PlayerStats {
  id: number;
  season_id: number;
  season_label: string;
  minutes: number;
  goals: number;
  assists: number;
}

interface Prediction {
  predicted_goals: number;
  predicted_assists: number;
  predicted_minutes: number;
  confidence_lower: number;
  confidence_upper: number;
}

export default function PlayerDetailPage() {
  const params = useParams();
  const playerId = Number(params.playerId);
  const [player, setPlayer] = useState<Player | null>(null);
  const [stats, setStats] = useState<PlayerStats[]>([]);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [predLoading, setPredLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      api.getPlayer(playerId),
      api.getPlayerStats(playerId),
    ]).then(([p, s]) => {
      setPlayer(p);
      setStats(s);
    }).finally(() => setLoading(false));
  }, [playerId]);

  async function getPrediction() {
    setPredLoading(true);
    try {
      const res = await api.predictPlayer(playerId, 0);
      setPrediction(res);
    } catch {
      alert("No stats available for prediction.");
    } finally {
      setPredLoading(false);
    }
  }

  if (loading) return (
    <main className="min-h-screen bg-gray-950 text-white p-8">
      <div className="text-center text-gray-400 py-12">Loading...</div>
    </main>
  );

  if (!player) return (
    <main className="min-h-screen bg-gray-950 text-white p-8">
      <div className="text-center text-red-400 py-12">Player not found.</div>
    </main>
  );

  const totalGoals = stats.reduce((sum, s) => sum + (s.goals || 0), 0);
  const totalAssists = stats.reduce((sum, s) => sum + (s.assists || 0), 0);
  const totalMinutes = stats.reduce((sum, s) => sum + (s.minutes || 0), 0);

  return (
    <main className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-900 rounded-xl p-8 border border-gray-800 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">{player.name}</h1>
              <p className="text-gray-400">{player.nationality}</p>
            </div>
            <span className="bg-green-900/50 text-green-400 px-3 py-1 rounded-full text-sm">
              {player.primary_position || "N/A"}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-6">
            <div className="bg-gray-800 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-green-400">{totalGoals}</p>
              <p className="text-gray-400 text-sm mt-1">Career Goals</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-blue-400">{totalAssists}</p>
              <p className="text-gray-400 text-sm mt-1">Career Assists</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-yellow-400">{Math.round(totalMinutes / 90)}</p>
              <p className="text-gray-400 text-sm mt-1">Appearances</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">XGBoost Prediction</h2>
            <button
              onClick={getPrediction}
              disabled={predLoading}
              className="bg-green-600 hover:bg-green-500 disabled:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {predLoading ? "Running..." : "Run Prediction"}
            </button>
          </div>
          {!prediction && (
            <p className="text-gray-500 text-sm">Click Run Prediction to get XGBoost-powered next season forecast.</p>
          )}
          {prediction && (
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-green-400">{prediction.predicted_goals}</p>
                <p className="text-gray-400 text-xs mt-1">Predicted Goals</p>
                <p className="text-gray-600 text-xs mt-1">{prediction.confidence_lower} – {prediction.confidence_upper} range</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-blue-400">{prediction.predicted_assists}</p>
                <p className="text-gray-400 text-xs mt-1">Predicted Assists</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-yellow-400">{Math.round(prediction.predicted_minutes / 90)}</p>
                <p className="text-gray-400 text-xs mt-1">Predicted Apps</p>
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-900 rounded-xl border border-gray-800">
          <div className="p-6 border-b border-gray-800">
            <h2 className="text-xl font-semibold">Season Stats</h2>
          </div>
          {stats.length === 0 ? (
            <div className="p-8 text-center text-gray-400">No stats available.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-400 border-b border-gray-800">
                    <th className="text-left p-4">Season</th>
                    <th className="text-center p-4">Minutes</th>
                    <th className="text-center p-4">Goals</th>
                    <th className="text-center p-4">Assists</th>
                    <th className="text-center p-4">G+A</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.map((s) => (
                    <tr key={s.id} className="border-b border-gray-800 hover:bg-gray-800">
                      <td className="p-4 text-gray-300">{s.season_label}</td>
                      <td className="p-4 text-center text-gray-300">{s.minutes || 0}</td>
                      <td className="p-4 text-center text-green-400 font-medium">{s.goals || 0}</td>
                      <td className="p-4 text-center text-blue-400 font-medium">{s.assists || 0}</td>
                      <td className="p-4 text-center text-yellow-400 font-medium">{(s.goals || 0) + (s.assists || 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

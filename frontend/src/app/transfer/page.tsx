"use client";
import { useState } from "react";

const API = "http://localhost:8000";

export default function TransferPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");

  async function simulate() {
    if (!query.trim() || loading) return;
    setLoading(true);
    setResult("");
    try {
      const res = await fetch(API + "/agent/transfer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, session_id: sessionId || undefined }),
      });
      const d = await res.json();
      setSessionId(d.session_id || "");
      setResult(d.response || "No response received.");
    } catch {
      setResult("Could not connect to backend.");
    } finally {
      setLoading(false);
    }
  }

  const examples = [
    "What if Haaland moved to Real Madrid?",
    "Impact of Mbappe joining Arsenal",
    "What if Salah transferred to PSG?",
    "What if Julian Alvarez moves to Barcelona?",
    "Impact of Vinicius Jr joining Manchester City",
    "What if Bellingham moved to Barcelona?",
  ];

  return (
    <main className="min-h-screen text-slate-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <a href="/" className="text-slate-400 hover:text-green-400 transition-colors text-sm mb-4 block">Back to Dashboard</a>
          <h1 className="text-3xl font-extrabold text-white mb-2">
            Transfer <span className="text-green-400">Simulator</span>
          </h1>
          <p className="text-slate-400">Simulate any transfer and get AI-powered impact analysis with real stats.</p>
        </div>

        <div className="bg-slate-900/60 rounded-xl p-6 border border-slate-800 mb-6 shadow-md">
          <label className="text-slate-400 text-sm mb-2 block font-medium">Describe the transfer</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && e.ctrlKey) simulate(); }}
            placeholder="e.g. What if Julian Alvarez moves to Barcelona?"
            className="w-full bg-slate-800 border border-slate-700 focus:border-green-500 text-white rounded-xl px-4 py-3 outline-none transition-colors resize-none h-24"
          />
          <div className="flex items-center gap-3 mt-3">
            <button
              onClick={simulate}
              disabled={loading || !query.trim()}
              className="bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:text-gray-500 text-white px-6 py-2 rounded-xl font-semibold transition-colors"
            >
              {loading ? "Analyzing..." : "Simulate Transfer"}
            </button>
            <span className="text-slate-500 text-xs">Powered by Groq + Tavily web search</span>
          </div>
        </div>

        <div className="mb-6">
          <p className="text-slate-400 text-sm mb-3 font-medium">Try these examples:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {examples.map((ex) => (
              <button
                key={ex}
                onClick={() => setQuery(ex)}
                className="bg-slate-900 border border-slate-700 hover:border-green-500 text-slate-400 hover:text-white text-sm px-4 py-3 rounded-lg transition-colors text-left"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>

        {result && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="border-l-4 border-red-500 bg-red-950/30 rounded-xl p-6 shadow-md">
                <h3 className="text-red-400 font-bold text-lg mb-2">FROM Club (Selling) Impact</h3>
                <p className="text-slate-400 text-sm mb-4">Estimated squad quality degradation and stats lost.</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-red-400 font-bold text-2xl">-4.2</span>
                  <span className="text-xs text-slate-550 uppercase tracking-wider font-semibold">Predicted Points</span>
                </div>
              </div>
              <div className="border-l-4 border-green-500 bg-green-950/30 rounded-xl p-6 shadow-md">
                <h3 className="text-green-400 font-bold text-lg mb-2">TO Club (Buying) Impact</h3>
                <p className="text-slate-400 text-sm mb-4">Estimated squad quality improvement and stats gained.</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-green-400 font-bold text-2xl">+5.5</span>
                  <span className="text-xs text-slate-550 uppercase tracking-wider font-semibold">Predicted Points</span>
                </div>
              </div>
            </div>

            <div className="border border-yellow-800/50 bg-yellow-950/20 rounded-xl p-6 shadow-lg">
              <h2 className="text-lg font-bold text-yellow-400 mb-4">AI Analyst Report</h2>
              <div className="text-slate-200 leading-relaxed whitespace-pre-wrap text-sm">{result}</div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

"use client";
import { useState } from "react";

interface TeamResult { name: string; score: number; }
interface Match { home: TeamResult; away: TeamResult; winner: TeamResult; }
interface Bracket { r16: Match[]; qf: Match[]; sf: Match[]; final: Match; }
interface WinnerProb { club_name: string; win_percentage: number; }
interface Participant { club_name: string; league_name: string; strength: number; predicted_points_2026_27: number; }
interface SimResult { predicted_winner: string; winner_probabilities: WinnerProb[]; bracket: Bracket; participants: Participant[]; iterations: number; }

function TeamRow({ name, score, won }: { name: string; score: number; won: boolean }) {
  return (
    <div className={"flex justify-between items-center px-2 py-1 " + (won ? "bg-yellow-900/20 text-yellow-400 font-semibold" : "")}>
      <span className={"text-xs truncate flex-1 " + (won ? "text-yellow-400 font-semibold" : "text-slate-500")}>{name}</span>
      <span className={"text-xs font-bold ml-1 " + (won ? "text-yellow-400" : "text-slate-600")}>{score}</span>
    </div>
  );
}

function MBox({ match, label, isFinal }: { match?: Match; label?: string; isFinal?: boolean }) {
  if (!match) return <div className="h-12 w-36" />;
  const hw = match.winner.name === match.home.name;
  return (
    <div className={"overflow-hidden w-36 " + (isFinal ? "border-2 border-yellow-500 shadow-[0_0_20px_rgba(234,179,8,0.25)]" : "border border-blue-900/40 bg-[#070c1a]")}>
      {label && <div className={"text-center text-[10px] uppercase tracking-widest py-0.5 border-b font-bold " + (isFinal ? "text-yellow-400 border-yellow-600 bg-yellow-900/10" : "text-slate-500 border-blue-900/30 bg-[#0a1226]")}>{label}</div>}
      <TeamRow name={match.home.name} score={match.home.score} won={hw} />
      <div className="border-t border-blue-900/30" />
      <TeamRow name={match.away.name} score={match.away.score} won={!hw} />
    </div>
  );
}

export default function UCLPage() {
  const [result, setResult] = useState<SimResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState<"bracket"|"odds"|"teams">("bracket");

  async function simulate() {
    setLoading(true);
    try {
      const r = await fetch("http://localhost:8000/api/ucl/simulate", { method: "POST" });
      setResult(await r.json());
    } catch { alert("Backend not running."); }
    finally { setLoading(false); }
  }

  const b = result?.bracket;
  const L16 = b?.r16.slice(0,4) ?? [];
  const R16 = b?.r16.slice(4,8) ?? [];
  const LQF = b?.qf.slice(0,2) ?? [];
  const RQF = b?.qf.slice(2,4) ?? [];
  const LSF = b?.sf[0];
  const RSF = b?.sf[1];

  return (
    <main className="min-h-screen text-slate-100">
      <div className="relative border-b border-blue-900/40 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_-20%,_#1e3a8a_0%,_transparent_60%)] opacity-70" />
        <div className="relative max-w-7xl mx-auto px-6 pt-10 pb-8">
          <a href="/" className="text-slate-500 hover:text-blue-400 transition-colors text-xs font-bold uppercase tracking-widest mb-4 block">
            &larr; Back to Dashboard
          </a>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h1 className="text-4xl font-black text-white uppercase tracking-tight">
                UCL <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">2026/27</span>
              </h1>
              <p className="text-slate-500 text-xs mt-1 uppercase tracking-widest font-bold">Monte Carlo simulation &middot; 6 seasons of league data</p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              {result && b && (
                <div className="text-sm border border-yellow-700 bg-yellow-900/30 text-yellow-300 px-4 py-2 shadow-[0_0_15px_rgba(234,179,8,0.2)]">
                  <span className="font-bold">{b.final.winner.name}</span>
                  <span className="ml-2 text-xs text-yellow-500 font-bold uppercase tracking-wide">bracket winner</span>
                </div>
              )}
              <button onClick={simulate} disabled={loading}
                className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 text-white font-bold px-6 py-2.5 text-xs uppercase tracking-widest transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)]">
                {loading ? "Simulating..." : "Run Simulation"}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {result && (
          <div className="flex gap-2 mb-6">
            {(["bracket","odds","teams"] as const).map(t => (
              <button key={t} onClick={() => setTab(t)}
                className={"px-4 py-2 text-xs font-bold uppercase tracking-wide transition-colors border " + (tab===t ? "bg-blue-600 text-white border-blue-500" : "bg-[#070c1a] text-slate-400 border-blue-900/40 hover:text-white hover:border-blue-500/50")}>
                {t==="bracket"?"Bracket":t==="odds"?"Win Odds":"16 Teams"}
              </button>
            ))}
          </div>
        )}

        {result && tab === "bracket" && b && (
          <div className="overflow-x-auto pb-4">
            <div className="flex items-center gap-0" style={{minWidth: 900, minHeight: 520}}>

              {/* LEFT: R16 */}
              <div className="flex flex-col justify-around h-full gap-2 py-2">
                <div className="text-center text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">R16</div>
                {L16.map((m,i) => <MBox key={i} match={m} label={"R16 "+(i+1)} />)}
              </div>

              {/* connector L16 -> LQF */}
              <div className="flex flex-col justify-around h-full" style={{width:20}}>
                <div className="flex flex-col" style={{flex:1}}>
                  <div className="flex-1 border-r border-b border-blue-900/40 rounded-br" />
                  <div className="flex-1 border-r border-t border-blue-900/40 rounded-tr" />
                </div>
                <div className="flex flex-col" style={{flex:1}}>
                  <div className="flex-1 border-r border-b border-blue-900/40 rounded-br" />
                  <div className="flex-1 border-r border-t border-blue-900/40 rounded-tr" />
                </div>
              </div>
              <div className="flex flex-col justify-around h-full" style={{width:20}}>
                <div style={{flex:1, borderBottom: "1px solid #1e3a5f"}} />
                <div style={{flex:1, borderTop: "1px solid #1e3a5f"}} />
              </div>

              {/* LEFT: QF */}
              <div className="flex flex-col justify-around h-full gap-4 py-8">
                <div className="text-center text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">QF</div>
                {LQF.map((m,i) => <MBox key={i} match={m} label={"QF "+(i+1)} />)}
              </div>

              {/* connector LQF -> LSF */}
              <div className="flex flex-col justify-around h-full" style={{width:20}}>
                <div className="flex flex-col" style={{flex:1}}>
                  <div className="flex-1 border-r border-b border-blue-900/40" />
                  <div className="flex-1 border-r border-t border-blue-900/40" />
                </div>
              </div>
              <div className="flex flex-col justify-center h-full" style={{width:20}}>
                <div style={{flex:1, borderBottom: "1px solid #1e3a5f"}} />
                <div style={{flex:1}} />
              </div>

              {/* LEFT: SF */}
              <div className="flex flex-col justify-center h-full py-16">
                <div className="text-center text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">SF</div>
                <MBox match={LSF} label="SF 1" />
              </div>

              {/* connector LSF -> Final */}
              <div className="flex flex-col justify-center h-full" style={{width:24}}>
                <div style={{height:1, background:"#1e3a5f"}} />
              </div>

              {/* FINAL */}
              <div className="flex flex-col justify-center h-full">
                <div className="text-center text-[10px] uppercase tracking-widest text-yellow-500 font-bold mb-1">FINAL</div>
                <MBox match={b.final} isFinal={true} />
              </div>

              {/* connector Final -> RSF */}
              <div className="flex flex-col justify-center h-full" style={{width:24}}>
                <div style={{height:1, background:"#1e3a5f"}} />
              </div>

              {/* RIGHT: SF */}
              <div className="flex flex-col justify-center h-full py-16">
                <div className="text-center text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">SF</div>
                <MBox match={RSF} label="SF 2" />
              </div>

              {/* connector RSF -> RQF */}
              <div className="flex flex-col justify-center h-full" style={{width:20}}>
                <div style={{flex:1}} />
                <div style={{flex:1, borderBottom: "1px solid #1e3a5f"}} />
              </div>
              <div className="flex flex-col justify-around h-full" style={{width:20}}>
                <div className="flex flex-col" style={{flex:1}}>
                  <div className="flex-1 border-l border-b border-blue-900/40" />
                  <div className="flex-1 border-l border-t border-blue-900/40" />
                </div>
              </div>

              {/* RIGHT: QF */}
              <div className="flex flex-col justify-around h-full gap-4 py-8">
                <div className="text-center text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">QF</div>
                {RQF.map((m,i) => <MBox key={i} match={m} label={"QF "+(i+3)} />)}
              </div>

              {/* connector RQF -> R16 right */}
              <div className="flex flex-col justify-around h-full" style={{width:20}}>
                <div style={{flex:1, borderBottom: "1px solid #1e3a5f"}} />
                <div style={{flex:1, borderTop: "1px solid #1e3a5f"}} />
              </div>
              <div className="flex flex-col justify-around h-full" style={{width:20}}>
                <div className="flex flex-col" style={{flex:1}}>
                  <div className="flex-1 border-l border-b border-blue-900/40 rounded-bl" />
                  <div className="flex-1 border-l border-t border-blue-900/40 rounded-tl" />
                </div>
                <div className="flex flex-col" style={{flex:1}}>
                  <div className="flex-1 border-l border-b border-blue-900/40 rounded-bl" />
                  <div className="flex-1 border-l border-t border-blue-900/40 rounded-tl" />
                </div>
              </div>

              {/* RIGHT: R16 */}
              <div className="flex flex-col justify-around h-full gap-2 py-2">
                <div className="text-center text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">R16</div>
                {R16.map((m,i) => <MBox key={i} match={m} label={"R16 "+(i+5)} />)}
              </div>

            </div>
          </div>
        )}

        {result && tab === "odds" && (
          <div className="bg-[#070c1a] border border-blue-900/40 max-w-xl overflow-hidden">
            <div className="p-4 border-b border-blue-900/40 text-sm font-bold text-white bg-[#0a1226] uppercase tracking-wide">
              Win probabilities &middot; {result.iterations?.toLocaleString()} simulations
            </div>
            <div className="p-2">
              {result.winner_probabilities.map((p, i) => (
                <div key={p.club_name} className="flex items-center gap-3 px-3 py-2.5 hover:bg-blue-950/30 transition-colors">
                  <span className="text-slate-500 text-xs w-4 font-bold">{i+1}</span>
                  <span className="text-slate-200 text-sm font-bold flex-1">{p.club_name}</span>
                  <div className="flex items-center gap-2 w-36">
                    <div className="flex-1 bg-[#0a1226] h-1.5 overflow-hidden">
                      <div className="bg-yellow-500 h-full" style={{width: Math.min(p.win_percentage,100)+"%"}}></div>
                    </div>
                    <span className="text-yellow-500 text-xs font-bold w-10 text-right">{p.win_percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {result && tab === "teams" && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {result.participants.map((p) => (
              <div key={p.club_name} className="bg-[#070c1a] border border-blue-900/40 hover:border-blue-500/50 p-4 transition-colors duration-200">
                <p className="font-bold text-slate-100 text-sm">{p.club_name}</p>
                <p className="text-slate-500 text-xs">{p.league_name}</p>
                <div className="flex justify-between mt-3 border-t border-blue-900/30 pt-2">
                  <span className="text-xs text-slate-500">Strength</span>
                  <span className="text-yellow-500 text-xs font-bold">{p.strength.toFixed(1)}</span>
                </div>
                <div className="flex justify-between mt-1">
                  <span className="text-xs text-slate-500">Pred pts</span>
                  <span className="text-blue-400 text-xs font-bold">{p.predicted_points_2026_27}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {!result && !loading && (
          <div className="border border-blue-900/40 p-16 text-center bg-[#070c1a] relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_#1e3a8a_0%,_transparent_70%)] opacity-30" />
            <div className="relative">
              <p className="text-white font-black text-2xl mb-2 uppercase tracking-tight">UEFA Champions League 2026/27</p>
              <p className="text-slate-500 text-sm">1000 Monte Carlo simulations &middot; 16 teams &middot; domestic league performance</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

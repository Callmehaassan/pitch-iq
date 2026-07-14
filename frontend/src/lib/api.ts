const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const res = await fetch(API_BASE + endpoint, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error("API error: " + res.status);
  return res.json();
}

export const api = {
  getLeagues: () => fetchAPI("/leagues/"),
  getLeagueStandings: (leagueId: number, seasonId: number) =>
    fetchAPI("/leagues/" + leagueId + "/standings?season_id=" + seasonId),
  getPlayers: (skip = 0, limit = 50, search = "", leagueId = 0) => {
    let url = "/players/?skip=" + skip + "&limit=" + limit;
    if (search) url += "&search=" + encodeURIComponent(search);
    if (leagueId) url += "&league_id=" + leagueId;
    return fetchAPI(url);
  },
  getPlayer: (playerId: number) => fetchAPI("/players/" + playerId),
  getPlayerStats: (playerId: number) => fetchAPI("/players/" + playerId + "/stats"),
  predictTeam: (clubId: number, seasonId: number) =>
    fetchAPI("/predict/league/" + clubId + "?season_id=" + seasonId),
  predictPlayer: (playerId: number, seasonId: number = 0) =>
    fetchAPI("/predict/player/" + playerId + "?season_id=" + seasonId),
  predictNextSeason: (leagueId: number) =>
    fetchAPI("/predict/next-season/" + leagueId),
  predictNextSeasonAll: () => fetchAPI("/predict/next-season"),
  getUCLTeamStrengths: () => fetchAPI("/api/ucl/team-strengths"),
  predictUCL: (iterations = 1000) =>
    fetchAPI("/api/ucl/predict?iterations=" + iterations),
  simulateUCL: (iterations = 1000) =>
    fetchAPI("/api/ucl/simulate?iterations=" + iterations, { method: "POST" }),
  askData: (query: string, sessionId?: string) =>
    fetchAPI("/agent/ask", {
      method: "POST",
      body: JSON.stringify({ query, session_id: sessionId }),
    }),
  getAnalystBrief: (fixtureId: number) =>
    fetchAPI("/agent/analyst/brief/" + fixtureId),
};

import type {
  FixtureCard,
  ComparePredictionResponse,
  TeamProfileResponse,
  HealthResponse,
  HealthStatusType,
} from "@/types";

const rawBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const sanitizedBase = rawBase.replace(/\/+$/, "");
const API_V1 = sanitizedBase.endsWith("/api/v1") ? sanitizedBase : `${sanitizedBase}/api/v1`;

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 6000): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}

export class ApiError extends Error {
  constructor(public status: number, message: string, public data?: unknown) {
    super(message);
    this.name = "ApiError";
  }
}

export interface ClientHealthStatus extends HealthResponse {
  derivedStatus: HealthStatusType;
}

export const api = {
  async getUpcomingFixtures(limit = 10): Promise<FixtureCard[]> {
    const res = await fetchWithTimeout(`${API_V1}/fixtures/upcoming?limit=${limit}`, { next: { revalidate: 60 } });
    if (!res.ok) throw new ApiError(res.status, "Failed to load upcoming fixtures");
    return res.json();
  },

  async getTeams(): Promise<string[]> {
    const res = await fetchWithTimeout(`${API_V1}/teams`, { next: { revalidate: 3600 } });
    if (!res.ok) throw new ApiError(res.status, "Failed to load teams");
    return res.json();
  },

  async getTeamProfile(teamName: string): Promise<TeamProfileResponse> {
    const res = await fetchWithTimeout(`${API_V1}/teams/${encodeURIComponent(teamName)}/profile`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) throw new ApiError(res.status, `Failed to load profile for ${teamName}`);
    return res.json();
  },

  async compareMatch(homeTeam: string, awayTeam: string): Promise<ComparePredictionResponse> {
    const res = await fetch(`${API_V1}/predictions/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ home_team: homeTeam, away_team: awayTeam }),
      cache: "no-store",
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new ApiError(res.status, errBody.detail || "Comparison failed", errBody);
    }
    return res.json();
  },

  async getHealth(): Promise<ClientHealthStatus> {
    try {
      const res = await fetch(`${API_V1}/health`, { cache: "no-store" });
      if (!res.ok) {
        return {
          status: "degraded",
          derivedStatus: "degraded",
          model_loaded: false,
          database_connected: false,
          fixtures_count: 0,
          models: {},
          message: `API returned HTTP ${res.status}`,
        };
      }
      const data: HealthResponse = await res.json();
      return {
        ...data,
        derivedStatus: data.status === "healthy" ? "healthy" : "degraded",
      };
    } catch {
      return {
        status: "offline",
        derivedStatus: "offline",
        model_loaded: false,
        database_connected: false,
        fixtures_count: 0,
        models: {},
        message: "API server unreachable",
      };
    }
  },
};

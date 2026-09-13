import { describe, it, expect, vi, beforeEach } from "vitest";
import { api, ApiError } from "../../src/lib/api";

describe("API Client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("getHealth returns healthy status on 200", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "healthy",
        model_loaded: true,
        database_connected: true,
        models: { dixon_coles: { loaded: true }, xgboost: { loaded: true } }
      })
    });

    const res = await api.getHealth();
    expect(res.status).toBe("healthy");
    expect(res.model_loaded).toBe(true);
  });

  it("getHealth returns offline when fetch rejects", async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error("Network connection dropped"));
    const res = await api.getHealth();
    expect(res.status).toBe("offline");
    expect(res.model_loaded).toBe(false);
  });
});

import { describe, it, expect, beforeAll, afterAll, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import { api } from "@/lib/api";
import { HealthBadge } from "@/components/common/HealthBadge";

const server = setupServer(
  http.get("http://localhost:8000/api/v1/health", () => {
    return HttpResponse.json({
      status: "healthy",
      model_loaded: true,
      database_connected: true,
      models: { dixon_coles: { loaded: true }, xgboost: { loaded: true } },
    });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("Resilience Matrix Integration Tests", () => {
  it("Scenario 1 (Nominal): returns healthy status badge", async () => {
    render(<HealthBadge />);
    await waitFor(() => {
      expect(screen.getByText("Models Live")).toBeDefined();
    });
  });

  it("Scenario 2 (Partial Model Outage): returns degraded badge when a model fails", async () => {
    server.use(
      http.get("http://localhost:8000/api/v1/health", () => {
        return HttpResponse.json({
          status: "degraded",
          model_loaded: true,
          database_connected: true,
          models: {
            dixon_coles: { loaded: true },
            xgboost: { loaded: false, error: "Gate 2A failed" },
          },
        });
      })
    );

    const res = await api.getHealth();
    expect(res.derivedStatus).toBe("degraded");
  });

  it("Scenario 3 (503 Service Unavailable): handles uninitialized models gracefully", async () => {
    server.use(
      http.get("http://localhost:8000/api/v1/health", () => {
        return new HttpResponse(null, { status: 503 });
      })
    );

    const res = await api.getHealth();
    expect(res.derivedStatus).toBe("degraded");
  });

  it("Scenario 4 (Network Offline): catches network drop and sets offline", async () => {
    server.use(
      http.get("http://localhost:8000/api/v1/health", () => {
        return HttpResponse.error();
      })
    );

    const res = await api.getHealth();
    expect(res.derivedStatus).toBe("offline");
  });

  it("Scenario 5 (Invalid Team 404): rejects invalid team comparison cleanly", async () => {
    server.use(
      http.post("http://localhost:8000/api/v1/predictions/compare", () => {
        return HttpResponse.json(
          { detail: "Unknown team 'Atlantis FC'" },
          { status: 404 }
        );
      })
    );

    await expect(api.compareMatch("Atlantis FC", "Chelsea")).rejects.toThrow(
      "Unknown team 'Atlantis FC'"
    );
  });
});

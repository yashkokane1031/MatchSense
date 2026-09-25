import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { HealthBadge } from "../../src/components/common/HealthBadge";
import * as healthHook from "../../src/hooks/useHealthStatus";

describe("HealthBadge", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders Models Live when healthy", () => {
    vi.spyOn(healthHook, "useHealthStatus").mockReturnValue({
      health: {
        status: "healthy",
        derivedStatus: "healthy",
        model_loaded: true,
        database_connected: true,
        fixtures_count: 380,
        models: { dixon_coles: { loaded: true } },
      },
      refetch: vi.fn(),
    });

    render(<HealthBadge />);
    expect(screen.getByText("Models Live")).toBeDefined();
  });

  it("renders System Degraded when degraded", () => {
    vi.spyOn(healthHook, "useHealthStatus").mockReturnValue({
      health: {
        status: "degraded",
        derivedStatus: "degraded",
        model_loaded: false,
        database_connected: true,
        fixtures_count: 0,
        models: {},
      },
      refetch: vi.fn(),
    });

    render(<HealthBadge />);
    expect(screen.getByText("System Degraded")).toBeDefined();
  });

  it("renders API Offline when offline", () => {
    vi.spyOn(healthHook, "useHealthStatus").mockReturnValue({
      health: {
        status: "offline",
        derivedStatus: "offline",
        model_loaded: false,
        database_connected: false,
        fixtures_count: 0,
        models: {},
      },
      refetch: vi.fn(),
    });

    render(<HealthBadge />);
    expect(screen.getByText("API Offline")).toBeDefined();
  });
});

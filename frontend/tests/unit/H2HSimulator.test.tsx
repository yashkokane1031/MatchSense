import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import SimulatorPage from "../../src/app/simulator/page";
import * as apiModule from "../../src/lib/api";

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams({ home: "Arsenal", away: "Chelsea" }),
  useRouter: () => ({ replace: vi.fn() }),
}));

describe("H2H Simulator", () => {
  it("hydrates teams from URL search params and calls compareMatch", async () => {
    const compareSpy = vi.spyOn(apiModule.api, "compareMatch").mockResolvedValue({
      home_team: "Arsenal",
      away_team: "Chelsea",
      dixon_coles: {
        prob_home: 0.48,
        prob_draw: 0.26,
        prob_away: 0.26,
        predicted_score: { home: 2, away: 1 },
        score_distribution: Array(5).fill(0).map(() => Array(5).fill(0.04))
      },
      xgboost: {
        prob_home: 0.52,
        prob_draw: 0.24,
        prob_away: 0.24,
        features: { elo_diff: 85, rest_days_diff: 2 }
      }
    });

    render(<SimulatorPage />);
    await waitFor(() => {
      expect(compareSpy).toHaveBeenCalledWith("Arsenal", "Chelsea");
    });
  });
});

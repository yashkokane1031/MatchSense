import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FixtureCard } from "../../src/components/fixtures/FixtureCard";
import type { FixtureCard as FixtureCardType } from "../../src/types";

describe("FixtureCard", () => {
  const mockFixture: FixtureCardType = {
    id: 101,
    gameweek: 28,
    kickoff_time: "2026-09-19T14:00:00Z",
    home_team: "Arsenal",
    away_team: "Chelsea",
    status: "SCHEDULED",
    predictions: {
      dixon_coles: { prob_home: 0.48, prob_draw: 0.26, prob_away: 0.26 },
      xgboost: { prob_home: 0.52, prob_draw: 0.24, prob_away: 0.24 }
    }
  };

  it("renders teams and links to simulator with query params", () => {
    render(<FixtureCard fixture={mockFixture} />);
    expect(screen.getByText("Arsenal")).toBeDefined();
    expect(screen.getByText("Chelsea")).toBeDefined();
    const link = screen.getByRole("link", { name: /simulate/i });
    expect(link.getAttribute("href")).toBe("/simulator?home=Arsenal&away=Chelsea");
  });
});

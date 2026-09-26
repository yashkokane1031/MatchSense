import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { PREMIER_LEAGUE_TEAMS, resolveTeamName } from "../../src/lib/constants";
import { TeamSelector } from "../../src/components/simulator/TeamSelector";
import SimulatorPage from "../../src/app/simulator/page";
import * as apiModule from "../../src/lib/api";

let mockSearchParams = new URLSearchParams({ home: "Arsenal", away: "Leeds" });

vi.mock("next/navigation", () => ({
  useSearchParams: () => mockSearchParams,
  useRouter: () => ({ replace: vi.fn() }),
}));

describe("Leeds United resolution & simulation suite", () => {
  beforeEach(() => {
    mockSearchParams = new URLSearchParams({ home: "Arsenal", away: "Leeds" });
  });

  it("resolves Leeds and case variations to canonical Leeds United", () => {
    expect(resolveTeamName("Leeds")).toBe("Leeds United");
    expect(resolveTeamName("leeds")).toBe("Leeds United");
    expect(resolveTeamName("Leeds United")).toBe("Leeds United");
    expect(resolveTeamName("leeds united fc")).toBe("Leeds United");
    expect(resolveTeamName("Leeds Utd")).toBe("Leeds United");
  });

  it("exposes all 27 model clubs including Leeds United in PREMIER_LEAGUE_TEAMS", () => {
    const keys = Object.keys(PREMIER_LEAGUE_TEAMS);
    expect(keys.length).toBe(27);
    expect(keys).toContain("Leeds United");
    expect(keys).toContain("West Ham United");
    expect(keys).toContain("Wolverhampton Wanderers");
    expect(keys).toContain("Burnley");
    expect(keys).toContain("Luton Town");
    expect(keys).toContain("Sheffield United");
    expect(keys).toContain("Sunderland");

    const meta = PREMIER_LEAGUE_TEAMS["Leeds United"];
    expect(meta).toBeDefined();
    expect(meta.shortName).toBe("LEE");
    expect(meta.primaryColor).toBe("#FFCD00");

    // Proxy lookup for alias
    const aliasMeta = PREMIER_LEAGUE_TEAMS["Leeds"];
    expect(aliasMeta).toBeDefined();
    expect(aliasMeta.shortName).toBe("LEE");
  });

  it("renders TeamSelector with awayTeam='Leeds' without falling back to Aston Villa", () => {
    render(
      <TeamSelector
        homeTeam="Arsenal"
        awayTeam="Leeds"
        onSelectHome={() => {}}
        onSelectAway={() => {}}
        onSwap={() => {}}
      />
    );

    const selects = screen.getAllByRole("combobox") as HTMLSelectElement[];
    const homeSelect = selects[0];
    const awaySelect = selects[1];

    expect(homeSelect.value).toBe("Arsenal");
    // Crucial bugfix check: must be Leeds United, never Aston Villa
    expect(awaySelect.value).toBe("Leeds United");
    expect(awaySelect.value).not.toBe("Aston Villa");

    // Check that Leeds United option is present in the select options
    const optionValues = Array.from(awaySelect.options).map((o) => o.value);
    expect(optionValues).toContain("Leeds United");
  });

  it("hydrates from query params '?home=Arsenal&away=Leeds' and calls compareMatch with ('Arsenal', 'Leeds United')", async () => {
    const compareSpy = vi.spyOn(apiModule.api, "compareMatch").mockResolvedValue({
      home_team: "Arsenal",
      away_team: "Leeds United",
      dixon_coles: {
        prob_home: 0.55,
        prob_draw: 0.25,
        prob_away: 0.20,
        predicted_score: { home: 1, away: 0 },
        score_distribution: Array(5).fill(0).map(() => Array(5).fill(0.04)),
      },
      xgboost: {
        prob_home: 0.53,
        prob_draw: 0.25,
        prob_away: 0.22,
        features: { elo_diff: 120, rest_days_diff: 1 },
      },
    });

    render(<SimulatorPage />);

    await waitFor(() => {
      expect(compareSpy).toHaveBeenCalledWith("Arsenal", "Leeds United");
    });
  });
});

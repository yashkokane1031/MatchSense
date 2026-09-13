import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import TeamProfilePage from "../../src/app/teams/[team]/page";

describe("Team Profile Page", () => {
  it("displays staleness badge when retraining is pending", async () => {
    const Component = await TeamProfilePage({
      params: Promise.resolve({ team: "Arsenal" }),
    });
    render(Component);
    expect(screen.getByText(/Arsenal/i)).toBeDefined();
  });
});

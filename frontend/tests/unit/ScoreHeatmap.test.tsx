import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ScoreHeatmap, computeCellAlpha } from "../../src/components/simulator/ScoreHeatmap";

describe("ScoreHeatmap Math & Rendering", () => {
  it("computeCellAlpha stays within [0.08, 0.90]", () => {
    const maxP = 0.12;
    expect(computeCellAlpha(0, maxP)).toBeCloseTo(0.08, 2);
    expect(computeCellAlpha(maxP, maxP)).toBeCloseTo(0.90, 2);
    expect(computeCellAlpha(0.04, maxP)).toBeGreaterThan(0.08);
    expect(computeCellAlpha(0.04, maxP)).toBeLessThan(0.90);
  });

  it("renders all 25 cells in 5x5 grid", () => {
    const grid = Array(5).fill(0).map(() => Array(5).fill(0.04));
    grid[2][1] = 0.12; // 2-1 max
    render(<ScoreHeatmap homeTeam="Arsenal" awayTeam="Chelsea" scoreDistribution={grid} />);
    const cells = screen.getAllByRole("gridcell");
    expect(cells).toHaveLength(25);
  });
});

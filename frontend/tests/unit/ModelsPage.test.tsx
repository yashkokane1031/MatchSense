import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ModelsPage from "../../src/app/models/page";

describe("ModelsPage", () => {
  it("renders walk-forward benchmark showcase with locked evaluation folds", () => {
    render(<ModelsPage />);

    expect(screen.getByText(/Model Architectures/i)).toBeDefined();
    expect(screen.getByText(/2023–24, 2024–25, and 2025–26 test folds/i)).toBeDefined();
    expect(screen.getByText("Dixon-Coles")).toBeDefined();
    expect(screen.getByText("XGBoost")).toBeDefined();
    expect(screen.getByText(/Bookmaker Odds/i)).toBeDefined();
    expect(screen.getByText(/Live Serving Pipeline/i)).toBeDefined();
  });
});

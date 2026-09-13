import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ModelProbabilityBar } from "../../src/components/common/ModelProbabilityBar";

describe("ModelProbabilityBar", () => {
  it("renders model name and formatted percentages", () => {
    render(
      <ModelProbabilityBar
        modelName="Dixon-Coles"
        probHome={0.523}
        probDraw={0.251}
        probAway={0.226}
      />
    );

    expect(screen.getByText("Dixon-Coles")).toBeDefined();
    expect(screen.getByText("52.3%")).toBeDefined();
    expect(screen.getByText("25.1%")).toBeDefined();
    expect(screen.getByText("22.6%")).toBeDefined();
  });

  it("handles XGBoost model styling and zero probability edge case safely", () => {
    render(
      <ModelProbabilityBar
        modelName="XGBoost"
        probHome={0.0}
        probDraw={0.5}
        probAway={0.5}
      />
    );

    expect(screen.getByText("XGBoost")).toBeDefined();
    expect(screen.getByText("0.0%")).toBeDefined();
    expect(screen.getAllByText("50.0%")).toHaveLength(2);
  });
});

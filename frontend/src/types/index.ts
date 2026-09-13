import type { components } from "./api.generated";

export type FixtureCard = components["schemas"]["FixtureCard"];
export type ComparePredictionResponse = components["schemas"]["ComparePredictionResponse"];
export type ModelPredictionBlock = components["schemas"]["ModelPredictionBlock"];
export type ScorePrediction = components["schemas"]["ScorePrediction"];
export type TeamProfileResponse = components["schemas"]["TeamProfileResponse"];
export type TeamStrength = components["schemas"]["TeamStrength"];
export type HealthResponse = components["schemas"]["HealthResponse"];
export type ModelStatus = components["schemas"]["ModelStatus"];

export type HealthStatusType = "healthy" | "degraded" | "offline";

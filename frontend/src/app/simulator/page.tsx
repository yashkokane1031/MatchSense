"use client";

import React, { useState, useEffect, useCallback, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { TeamSelector } from "@/components/simulator/TeamSelector";
import { ModelComparisonBlock } from "@/components/simulator/ModelComparisonBlock";
import type { ComparePredictionResponse } from "@/types";

function SimulatorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [homeTeam, setHomeTeam] = useState<string>(
    searchParams.get("home") || "Arsenal"
  );
  const [awayTeam, setAwayTeam] = useState<string>(
    searchParams.get("away") || "Chelsea"
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ComparePredictionResponse | null>(null);
  const cacheRef = useRef<Map<string, ComparePredictionResponse>>(new Map());

  const runSimulation = useCallback(async (h: string, a: string) => {
    if (!h || !a || h === a) return;
    const cacheKey = `${h}:${a}`;
    if (cacheRef.current.has(cacheKey)) {
      setData(cacheRef.current.get(cacheKey)!);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await api.compareMatch(h, a);
      cacheRef.current.set(cacheKey, res);
      setData(res);
    } catch (err: unknown) {
      const fallback: ComparePredictionResponse = {
        home_team: h,
        away_team: a,
        dixon_coles: {
          prob_home: 0.48,
          prob_draw: 0.26,
          prob_away: 0.26,
          predicted_score: { home: 2, away: 1 },
          score_distribution: [
            [0.05, 0.08, 0.05, 0.02, 0.01],
            [0.08, 0.11, 0.08, 0.03, 0.01],
            [0.06, 0.12, 0.07, 0.03, 0.01],
            [0.03, 0.05, 0.04, 0.02, 0.01],
            [0.01, 0.02, 0.01, 0.01, 0.00],
          ],
        },
        xgboost: {
          prob_home: 0.51,
          prob_draw: 0.25,
          prob_away: 0.24,
          features: {
            elo_diff: 65,
            form_pts_diff: 4,
            sot_diff: 1.8,
            rest_days_diff: 2,
          },
        },
      };
      setData(fallback);
      const msg =
        err instanceof Error
          ? err.message
          : "Operating offline: displaying research simulation snapshot. Live FastAPI backend is offline.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    runSimulation(homeTeam, awayTeam);
  }, [homeTeam, awayTeam, runSimulation]);

  const handleSwap = () => {
    const nextHome = awayTeam;
    const nextAway = homeTeam;
    setHomeTeam(nextHome);
    setAwayTeam(nextAway);
    router.replace(
      `/simulator?home=${encodeURIComponent(nextHome)}&away=${encodeURIComponent(nextAway)}`,
      { scroll: false }
    );
  };

  const handleSelectHome = (team: string) => {
    setHomeTeam(team);
    router.replace(
      `/simulator?home=${encodeURIComponent(team)}&away=${encodeURIComponent(awayTeam)}`,
      { scroll: false }
    );
  };

  const handleSelectAway = (team: string) => {
    setAwayTeam(team);
    router.replace(
      `/simulator?home=${encodeURIComponent(homeTeam)}&away=${encodeURIComponent(team)}`,
      { scroll: false }
    );
  };

  return (
    <div>
      <div className="mb-8 text-center sm:text-left">
        <h1 className="text-3xl font-extrabold text-white">
          Head-to-Head <span className="text-cyan-400">Match Simulator</span>
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Select any two Premier League clubs to run live side-by-side Poisson scoreline distributions and XGBoost feature differentials.
        </p>
      </div>

      <TeamSelector
        homeTeam={homeTeam}
        awayTeam={awayTeam}
        onSelectHome={handleSelectHome}
        onSelectAway={handleSelectAway}
        onSwap={handleSwap}
      />

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/30 text-rose-300 text-sm mb-6">
          {error}
        </div>
      )}

      {loading && !data && (
        <div className="text-center py-20 text-slate-500 animate-pulse font-mono">
          Running dual-model simulation...
        </div>
      )}

      {data && (
        <ModelComparisonBlock
          data={data}
          homeTeam={homeTeam}
          awayTeam={awayTeam}
        />
      )}
    </div>
  );
}

export default function SimulatorPage() {
  return (
    <Suspense
      fallback={
        <div className="text-center py-20 text-slate-500 font-mono">
          Loading simulator...
        </div>
      }
    >
      <SimulatorContent />
    </Suspense>
  );
}

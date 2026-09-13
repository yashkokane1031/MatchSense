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
      const msg = err instanceof Error ? err.message : "Failed to calculate simulation";
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

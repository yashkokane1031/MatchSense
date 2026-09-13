import { api } from "@/lib/api";
import { GameweekHero } from "@/components/fixtures/GameweekHero";
import { FixtureGrid } from "@/components/fixtures/FixtureGrid";
import type { FixtureCard } from "@/types";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let fixtures: FixtureCard[] = [];
  let fetchError: string | null = null;

  try {
    fixtures = await api.getUpcomingFixtures();
  } catch (err) {
    console.error("Failed to load upcoming fixtures:", err);
    fetchError = "Unable to connect to MatchSense API server. Displaying historical mock snapshot.";
  }

  return (
    <div className="space-y-6">
      <GameweekHero fixtures={fixtures} />

      {fetchError && (
        <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-300 text-xs flex items-center gap-3">
          <span className="w-2 h-2 rounded-full bg-amber-400" />
          <span>{fetchError}</span>
        </div>
      )}

      {fixtures.length === 0 && !fetchError ? (
        <div className="text-center py-20 bg-[#111622]/40 rounded-2xl border border-white/5">
          <p className="text-slate-400">No scheduled fixtures available. Sync pipeline runs weekly.</p>
        </div>
      ) : (
        <FixtureGrid initialFixtures={fixtures} />
      )}
    </div>
  );
}

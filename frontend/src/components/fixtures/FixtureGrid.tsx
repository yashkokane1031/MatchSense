"use client";

import { useState, useMemo } from "react";
import type { FixtureCard as FixtureCardType } from "@/types";
import { FixtureCard } from "./FixtureCard";
import { FixtureFilter } from "./FixtureFilter";

interface FixtureGridProps {
  initialFixtures: FixtureCardType[];
}

export function FixtureGrid({ initialFixtures }: FixtureGridProps) {
  const [selectedTeam, setSelectedTeam] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState<string>("");

  const filteredFixtures = useMemo(() => {
    return initialFixtures.filter((fixture) => {
      const matchesTeam =
        selectedTeam === "ALL" ||
        fixture.home_team === selectedTeam ||
        fixture.away_team === selectedTeam;

      const q = searchTerm.toLowerCase().trim();
      const matchesSearch =
        !q ||
        fixture.home_team.toLowerCase().includes(q) ||
        fixture.away_team.toLowerCase().includes(q);

      return matchesTeam && matchesSearch;
    });
  }, [initialFixtures, selectedTeam, searchTerm]);

  return (
    <div>
      <FixtureFilter
        selectedTeam={selectedTeam}
        onSelectTeam={setSelectedTeam}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
      />

      {filteredFixtures.length === 0 ? (
        <div className="text-center py-16 bg-[#111622]/40 rounded-2xl border border-white/5">
          <p className="text-slate-400 text-sm">
            No fixtures match the selected filter. Try choosing &quot;All Clubs&quot;.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filteredFixtures.map((fixture) => (
            <FixtureCard key={fixture.id} fixture={fixture} />
          ))}
        </div>
      )}
    </div>
  );
}

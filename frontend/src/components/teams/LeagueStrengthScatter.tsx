"use client";

import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface TeamScatterPoint {
  team: string;
  attack: number;
  defense: number;
}

export function LeagueStrengthScatter({
  points,
}: {
  points: TeamScatterPoint[];
}) {
  return (
    <div className="w-full h-80 bg-[#111622]/60 p-4 rounded-2xl border border-white/5">
      <div className="text-xs text-slate-400 mb-2 flex justify-between">
        <span>Attack Strength (α) →</span>
        <span>Defense Rating (β, Lower is Better)</span>
      </div>
      <ResponsiveContainer width="100%" height="90%">
        <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.05)" />
          <XAxis
            type="number"
            dataKey="attack"
            name="Attack"
            domain={["auto", "auto"]}
            stroke="#64748b"
            tick={{ fontSize: 11 }}
          />
          <YAxis
            type="number"
            dataKey="defense"
            name="Defense"
            domain={["auto", "auto"]}
            reversed
            stroke="#64748b"
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            content={({ payload }) => {
              if (!payload || payload.length === 0) return null;
              const data = payload[0].payload as TeamScatterPoint;
              return (
                <div className="bg-slate-900 border border-white/10 p-2.5 rounded-lg text-xs font-mono text-white shadow-xl">
                  <p className="font-bold text-cyan-400">{data.team}</p>
                  <p>Attack (α): {data.attack.toFixed(2)}</p>
                  <p>Defense (β): {data.defense.toFixed(2)}</p>
                </div>
              );
            }}
          />
          <Scatter name="Clubs" data={points} fill="#0ea5e9" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

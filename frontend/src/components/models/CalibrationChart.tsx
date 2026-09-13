"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

export interface CalibrationBin {
  predicted: number;
  observed_dc: number;
  observed_xgb: number;
  ideal: number;
}

export function CalibrationChart({ bins }: { bins: CalibrationBin[] }) {
  return (
    <div className="w-full h-80 bg-[#111622]/80 p-5 rounded-2xl border border-white/10">
      <h4 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">
        Reliability Diagram (Calibration Curves)
      </h4>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={bins} margin={{ top: 5, right: 20, bottom: 5, left: -10 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="predicted"
            stroke="#64748b"
            tick={{ fontSize: 11 }}
            domain={[0, 1]}
          />
          <YAxis
            stroke="#64748b"
            tick={{ fontSize: 11 }}
            domain={[0, 1]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid rgba(255,255,255,0.1)",
              fontSize: "12px",
              borderRadius: "8px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
          <Line
            type="monotone"
            dataKey="ideal"
            name="Ideal (y=x)"
            stroke="#475569"
            strokeDasharray="3 3"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="observed_dc"
            name="Dixon-Coles"
            stroke="#0ea5e9"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
          <Line
            type="monotone"
            dataKey="observed_xgb"
            name="XGBoost"
            stroke="#8b5cf6"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

import benchmarks from "@/data/benchmarks.json";
import { CalibrationChart } from "@/components/models/CalibrationChart";

export const dynamic = "force-dynamic";

export default function ModelsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white">
          Model Architectures & <span className="text-cyan-400">Walk-Forward Evaluation</span>
        </h1>
        <p className="text-slate-400 text-sm mt-1 max-w-2xl">
          Rigorous out-of-sample statistical evaluation comparing generative Poisson and discriminative tree classifiers against bookmaker baselines across 3 rolling Premier League test seasons.
        </p>
      </div>

      {/* Honest Research Snapshot Banner */}
      <div className="p-4 rounded-2xl bg-cyan-950/30 border border-cyan-500/30 text-cyan-300 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2 font-mono">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span>Out-of-sample walk-forward evaluation locked to 2023–24, 2024–25, and 2025–26 test folds.</span>
        </div>
        <span className="text-slate-400">Frozen Snapshot: {benchmarks.evaluated_at}</span>
      </div>

      {/* Benchmark Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300 bg-[#111622]/80 rounded-2xl border border-white/10 overflow-hidden">
          <thead className="text-xs uppercase bg-white/5 text-slate-400 font-mono">
            <tr>
              <th className="p-4">Model Architecture</th>
              <th className="p-4">Paradigm</th>
              <th className="p-4">Ranked Prob Score (RPS) ↓</th>
              <th className="p-4">Brier Score ↓</th>
              <th className="p-4">Log-Loss ↓</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-mono text-xs">
            <tr className="hover:bg-white/5 transition-colors">
              <td className="p-4 font-bold text-cyan-400">Dixon-Coles</td>
              <td className="p-4 text-slate-400">Generative (Poisson, ξ=0.005, ρ)</td>
              <td className="p-4 font-bold text-white">
                {benchmarks.metrics.dixon_coles.rps.toFixed(4)}
              </td>
              <td className="p-4">{benchmarks.metrics.dixon_coles.brier.toFixed(3)}</td>
              <td className="p-4">{benchmarks.metrics.dixon_coles.log_loss.toFixed(3)}</td>
            </tr>
            <tr className="hover:bg-white/5 transition-colors">
              <td className="p-4 font-bold text-violet-400">XGBoost</td>
              <td className="p-4 text-slate-400">Discriminative (Elo, Form, SOT)</td>
              <td className="p-4 font-bold text-white">
                {benchmarks.metrics.xgboost.rps.toFixed(4)}
              </td>
              <td className="p-4">{benchmarks.metrics.xgboost.brier.toFixed(3)}</td>
              <td className="p-4">{benchmarks.metrics.xgboost.log_loss.toFixed(3)}</td>
            </tr>
            <tr className="hover:bg-white/5 transition-colors bg-emerald-950/10">
              <td className="p-4 font-bold text-emerald-400">Bookmaker Odds (Benchmark)</td>
              <td className="p-4 text-slate-400">Market Implied Probabilities</td>
              <td className="p-4 font-bold text-emerald-400">
                {benchmarks.metrics.bookmakers.rps.toFixed(4)}
              </td>
              <td className="p-4">{benchmarks.metrics.bookmakers.brier.toFixed(3)}</td>
              <td className="p-4">{benchmarks.metrics.bookmakers.log_loss.toFixed(3)}</td>
            </tr>
            <tr className="hover:bg-white/5 transition-colors text-slate-500">
              <td className="p-4">Always Home (Naive)</td>
              <td className="p-4">Static Baseline</td>
              <td className="p-4">{benchmarks.metrics.naive_home.rps.toFixed(4)}</td>
              <td className="p-4">{benchmarks.metrics.naive_home.brier.toFixed(3)}</td>
              <td className="p-4">{benchmarks.metrics.naive_home.log_loss.toFixed(3)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <CalibrationChart bins={benchmarks.calibration_bins} />
        <div className="p-6 rounded-2xl bg-[#111622]/80 border border-white/10 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-white mb-2">Live Serving Pipeline</h3>
            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              Automated GitHub Actions weekly sync engine fetches live fixtures, executes decoupled model fitting, runs Gate 2A parameter bounds verification, and triggers zero-downtime hot-reloads via atomic pointer swapping.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 font-mono text-xs text-slate-300 space-y-1.5">
            <p>• Model Reload Cadence: 30s TTL Database Polling</p>
            <p>• Hot-Reload Mechanism: Atomic Pointer Swap</p>
            <p>• Retrying Optimization Budget: 2 Attempts (Attempt 2 maxfun=100,000)</p>
            <p>• Evaluation Folds: 2023–24, 2024–25, 2025–26 (Walk-Forward)</p>
          </div>
        </div>
      </div>
    </div>
  );
}

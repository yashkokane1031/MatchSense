"""Comprehensive evaluation scorecard generator."""

from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationReport:
    """Container for model evaluation results, cross-validation, significance, and backtesting."""

    model_name: str
    folds: list[dict[str, Any]]
    aggregate_metrics: dict[str, float]
    significance_results: dict[str, Any]
    backtest_results: dict[str, Any]
    calibration_results: dict[str, Any]

    def to_markdown(self) -> str:
        """Generate full GitHub-flavored Markdown scorecard."""
        lines: list[str] = [
            f"# MatchSense — Model Evaluation Report: `{self.model_name}`\n",
            "## 1. Out-of-Sample Performance by Season (Rolling 4-Season Window)\n",
            "| Season | Matches | RPS | Brier Score | Log-Loss | Accuracy |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ]

        tot_matches = 0
        for f in self.folds:
            n_m = int(f.get("n_matches", 0))
            tot_matches += n_m
            lines.append(
                f"| **{f.get('season', 'Unknown')}** | {n_m:,} | "
                f"{f.get('rps', 0.0):.4f} | {f.get('brier', 0.0):.4f} | "
                f"{f.get('log_loss', 0.0):.4f} | {f.get('accuracy', 0.0):.1%} |"
            )

        agg = self.aggregate_metrics
        if self.folds or agg:
            lines.append(
                f"| **Aggregate** | **{tot_matches:,}** | "
                f"**{agg.get('rps', 0.0):.4f}** | **{agg.get('brier', 0.0):.4f}** | "
                f"**{agg.get('log_loss', 0.0):.4f}** | **{agg.get('accuracy', 0.0):.1%}** |\n"
            )

        # 2. Significance Testing
        if self.significance_results:
            lines.append("## 2. Statistical Significance vs Baselines (Primary: Per-Fold Independent)\n")

            if "per_fold" in self.significance_results:
                per_fold = self.significance_results["per_fold"]
                for season, comp_dict in per_fold.items():
                    lines.append(f"### Fold Season: `{season}`\n")
                    lines.append("| Comparison | Metric | Test | Stat | p-value | Interpretation |")
                    lines.append("| :--- | :--- | :--- | :---: | :---: | :--- |")
                    for comp_name, tests in comp_dict.items():
                        w = tests.get("wilcoxon")
                        if w:
                            w_stat = getattr(w, "statistic", w.get("statistic", 0.0) if isinstance(w, dict) else 0.0)
                            w_p = getattr(w, "p_value", w.get("p_value", 1.0) if isinstance(w, dict) else 1.0)
                            sig = "p < 0.05 *" if w_p < 0.05 else "not significant"
                            lines.append(f"| vs {comp_name} | RPS | Wilcoxon (Pratt) | W={w_stat:.1f} | {w_p:.4f} | {sig} |")
                        m = tests.get("mcnemar")
                        if m:
                            m_stat = getattr(m, "statistic", m.get("statistic", 0.0) if isinstance(m, dict) else 0.0)
                            m_p = getattr(m, "p_value", m.get("p_value", 1.0) if isinstance(m, dict) else 1.0)
                            is_exact = getattr(m, "is_exact", m.get("is_exact", False) if isinstance(m, dict) else False)
                            test_name = "McNemar (Exact)" if is_exact else "McNemar (Chi2)"
                            sig = "p < 0.05 *" if m_p < 0.05 else "not significant"
                            lines.append(f"| vs {comp_name} | Accuracy | {test_name} | stat={m_stat:.1f} | {m_p:.4f} | {sig} |")
                    lines.append("")

            if "pooled" in self.significance_results:
                pooled = self.significance_results["pooled"]
                caveat = pooled.get(
                    "caveat",
                    "The pooled 1,140-match significance test combines overlapping training windows across adjacent seasons; "
                    "per-fold test statistics provide the primary independent verification.",
                )
                lines.append("### Pooled 3-Season Performance (Descriptive)\n")
                lines.append(f"> [!NOTE]\n> **Caveat**: {caveat}\n")
                lines.append("| Comparison | Metric | Test | Stat | p-value | Interpretation |")
                lines.append("| :--- | :--- | :--- | :---: | :---: | :--- |")
                pooled_tests = pooled.get("results", {})
                for comp_name, tests in pooled_tests.items():
                    w = tests.get("wilcoxon")
                    if w:
                        w_stat = getattr(w, "statistic", w.get("statistic", 0.0) if isinstance(w, dict) else 0.0)
                        w_p = getattr(w, "p_value", w.get("p_value", 1.0) if isinstance(w, dict) else 1.0)
                        sig = "p < 0.05 *" if w_p < 0.05 else "not significant"
                        lines.append(f"| vs {comp_name} | RPS | Wilcoxon (Pratt) | W={w_stat:.1f} | {w_p:.4f} | {sig} |")
                    m = tests.get("mcnemar")
                    if m:
                        m_stat = getattr(m, "statistic", m.get("statistic", 0.0) if isinstance(m, dict) else 0.0)
                        m_p = getattr(m, "p_value", m.get("p_value", 1.0) if isinstance(m, dict) else 1.0)
                        is_exact = getattr(m, "is_exact", m.get("is_exact", False) if isinstance(m, dict) else False)
                        test_name = "McNemar (Exact)" if is_exact else "McNemar (Chi2)"
                        sig = "p < 0.05 *" if m_p < 0.05 else "not significant"
                        lines.append(f"| vs {comp_name} | Accuracy | {test_name} | stat={m_stat:.1f} | {m_p:.4f} | {sig} |")
                lines.append("")
            elif "per_fold" not in self.significance_results:
                # Flat format
                lines.append("> *Caveat: Per-fold independent tests provide primary evidence; pooled statistics are descriptive.*\n")
                lines.append("| Comparison | Metric | Test | Stat | p-value | Interpretation |")
                lines.append("| :--- | :--- | :--- | :---: | :---: | :--- |")
                for comp_name, tests in self.significance_results.items():
                    w = tests.get("wilcoxon")
                    if w:
                        w_stat = getattr(w, "statistic", w.get("statistic", 0.0) if isinstance(w, dict) else 0.0)
                        w_p = getattr(w, "p_value", w.get("p_value", 1.0) if isinstance(w, dict) else 1.0)
                        sig = "p < 0.05 *" if w_p < 0.05 else "not significant"
                        lines.append(f"| vs {comp_name} | RPS | Wilcoxon (Pratt) | W={w_stat:.1f} | {w_p:.4f} | {sig} |")
                    m = tests.get("mcnemar")
                    if m:
                        m_stat = getattr(m, "statistic", m.get("statistic", 0.0) if isinstance(m, dict) else 0.0)
                        m_p = getattr(m, "p_value", m.get("p_value", 1.0) if isinstance(m, dict) else 1.0)
                        is_exact = getattr(m, "is_exact", m.get("is_exact", False) if isinstance(m, dict) else False)
                        test_name = "McNemar (Exact)" if is_exact else "McNemar (Chi2)"
                        sig = "p < 0.05 *" if m_p < 0.05 else "not significant"
                        lines.append(f"| vs {comp_name} | Accuracy | {test_name} | stat={m_stat:.1f} | {m_p:.4f} | {sig} |")
                lines.append("")

        # 3. Financial Simulation
        if self.backtest_results:
            lines.extend([
                "## 3. Financial Simulation & ROI (Edge >= 5%)\n",
                "| Odds Source | Staking | Bets | Turnover | Net PnL | ROI % | Win % | Max DD % | Annual Sharpe |",
                "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
            ])
            for _, b in self.backtest_results.items():
                lines.append(
                    f"| {b.get('odds_source', 'N/A')} | {b.get('staking', 'N/A')} | "
                    f"{b.get('total_bets', 0):,} | {b.get('turnover', 0.0):.1f}u | "
                    f"{b.get('net_pnl', 0.0):+.1f}u | {b.get('roi', 0.0):+.1f}% | "
                    f"{b.get('win_rate', 0.0):.1%} | {b.get('max_drawdown_pct', 0.0):.1f}% | "
                    f"{b.get('annualized_sharpe', 0.0):.2f} |"
                )
            lines.append("")

        # 4. Calibration
        if self.calibration_results:
            cal = self.calibration_results
            lines.extend([
                "## 4. Calibration & Reliability Summary\n",
                f"- **Overall ECE**: `{cal.get('ece_overall', 0.0):.4f}` ({cal.get('ece_overall', 0.0):.1%})",
                f"- **Home ECE / MCE**: `{cal.get('ece_home', 0.0):.4f}` / `{cal.get('mce_home', 0.0):.4f}`",
                f"- **Draw ECE / MCE**: `{cal.get('ece_draw', 0.0):.4f}` / `{cal.get('mce_draw', 0.0):.4f}`",
                f"- **Away ECE / MCE**: `{cal.get('ece_away', 0.0):.4f}` / `{cal.get('mce_away', 0.0):.4f}`",
                "",
            ])

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert report metrics into a flattened dictionary."""
        flat: dict[str, Any] = {"model_name": self.model_name}
        for k, v in self.aggregate_metrics.items():
            flat[f"aggregate_{k}"] = v
        for i, f in enumerate(self.folds):
            for k, v in f.items():
                flat[f"fold_{i}_{k}"] = v
        if self.calibration_results:
            for k, v in self.calibration_results.items():
                if isinstance(v, (int, float, str, bool)):
                    flat[f"calibration_{k}"] = v
        return flat

    def print_summary(self) -> None:
        """Print markdown report to stdout."""
        print(self.to_markdown())

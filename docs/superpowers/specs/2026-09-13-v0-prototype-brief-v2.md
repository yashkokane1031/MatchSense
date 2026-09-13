# MatchSense V2 — "Tactical Pitch Telemetry" Prototype Brief

> **Version**: V2 Prototype Specification  
> **Skill Invocation**: `frontend-design`  
> **Animation Engine**: `motion` (`motion.dev` / `motion/react`)  
> **Design Thesis**: Move beyond generic SaaS dashboards into an unforgettable, high-end European football tactical intelligence terminal — fusing Bloomberg-level analytical density with stadium floodlight telemetry aesthetics.  
> **Target**: Copy-pasteable into Vercel v0 with interactive mock data.

---

## What Elevates V2 Over V1

| Dimension | V1 (Baseline Prototype) | V2 ("Tactical Pitch Telemetry" Edition) |
|---|---|---|
| **Aesthetic Direction** | Clean standard dark-mode SaaS dashboard. | **Tactical Match Intelligence Room**: Pitch-midnight carbon base, subtle tactical field coordinate crosshairs, floodlight ambient glow, frosted glass with tinted neon rim-lighting. |
| **Typography** | Generic `Inter` + monospace. | **`Clash Display` / `Cabinet Grotesk`** (muscular, geometric European sports editorial display font) paired with **`Plus Jakarta Sans`** for body and **`Geist Mono`** for glowing numerical metrics. |
| **Motion (`motion.dev`)** | Static CSS flex transitions only. | **Fluid Spring Physics**: Staggered card reveals, fluid sliding tab pills via `layoutId`, 3D interactive heatmap cell springs (`whileHover={{ scale: 1.12 }}`), rotating team swap triggers (`whileTap={{ rotate: 180 }}`), and breathing scoreline auroras. |
| **Model Separation** | Flat color tags. | **Distinct Visual Identity Engines**: Dixon-Coles **Cyan Pulse** (`#00F2FE` $\rightarrow$ `#4FACFE`) vs. XGBoost **Ultraviolet Matrix** (`#7928CA` $\rightarrow$ `#B800FF`), completely disambiguated from match outcomes (Stadium Emerald, Tactical Silver, Hyper Amber). |
| **Information Density** | Static cards with text. | **Telemetry HUD Feel**: Live ticker ribbon, divergence meter ($\Delta \text{Prob}$ highlighting where the models disagree most), and interactive quadrant filters. |

---

## v0 Copy-Paste Prompt (V2)

```markdown
You are building the V2 UI prototype for "MatchSense", an elite sports analytics and match intelligence platform for the Premier League. MatchSense serves dual competing models: Dixon-Coles (Generative Bivariate Poisson) and XGBoost (Discriminative Gradient Boosted Trees).

The visual goal for V2 is an unforgettable, high-end "Tactical Pitch Telemetry" aesthetic — inspired by modern Formula 1 telemetry dashboards and Opta Analyst war-rooms. No generic "AI slop" or cookie-cutter SaaS layouts. Use Tailwind CSS, Lucide icons, Radix UI primitives, and Motion (from motion.dev / `motion/react`) for spring animations and layout transitions.

This is a front-of-the-frontend prototype with rich mock data to evaluate aesthetic quality, fluid motion, and layout dynamics.

---

### 1. Distinctive Visual Identity & Tokens

* **Surfaces & Atmosphere**:
  - Root Background: Deep Stadium Carbon (`#05070B` to `#080C14` radial gradient).
  - Tactical Grid Texture: Subtle background overlay with 40px tactical crosshairs and pitch boundary lines at 4% opacity.
  - Glassmorphic Cards: `background: rgba(12, 17, 29, 0.7)`, border `1px solid rgba(255, 255, 255, 0.07)`, `backdrop-filter: blur(16px)`, with a subtle top-edge rim glow.
* **Typography**:
  - Display / Big Headlines: `Clash Display` or `Cabinet Grotesk` (bold, geometric, authoritative sports editorial typography).
  - Body Text: `Plus Jakarta Sans` (crisp, readable neutral).
  - Metrics, Odds, Probabilities: `Geist Mono` / `JetBrains Mono` with `tabular-nums tracking-tight` and glowing text accents.
* **Color Hierarchy (Zero Hue Collision)**:
  - **Dixon-Coles Model (Generative Poisson)**: Electric Cyan Pulse (`#00F2FE` gradient to `#00A8FF`). Glow: `rgba(0, 242, 254, 0.2)`.
  - **XGBoost Model (Discriminative ML)**: Ultraviolet Matrix (`#9D00FF` gradient to `#6B00FF`). Glow: `rgba(157, 0, 255, 0.2)`.
  - **Match Outcomes (Probabilities)**:
    - Home Win: **Stadium Emerald** (`#00E676`)
    - Draw: **Tactical Silver/Zinc** (`#8E9AA8`)
    - Away Win: **Hyper Amber** (`#FF9100`)
    *(Strict Rule: The model identity colors Cyan and Violet must never be used for outcome segments).*

---

### 2. Global Navigation & Telemetry Ribbon

* **Top Telemetry Bar**:
  - A slim 28px ticker ribbon across the very top:
    - `● SERVING LAYER: 30s TTL Hot-Reload Active`
    - `KICKOFF WINDOW: GW28 Starts in 2d 14h 22m`
    - `DIVERGENCE INDEX: High disagreement in 2 of 10 fixtures`
* **Main Header & Navigation**:
  - Brand: **Match<span className="text-cyan-400">Sense</span>** with a tactical pitch coordinate icon.
  - Interactive Tabs with Motion (`motion.dev`):
    - Tabs: `Gameweek Telemetry` (`/`), `H2H Matchup Lab` (`/simulator`), `Club Dossier` (`/teams`), `Model Observatory` (`/models`).
    - Use `motion.div` with `layoutId="activeTabPill"` for a fluid, spring-animated sliding background pill (`bg-white/10 rounded-full border border-white/15`) when switching routes.
  - Right: System Status Pill:
    - `● MODELS LIVE` (pulsing emerald beacon, dark obsidian capsule with emerald neon ring).

---

### 3. Four Dedicated Route Prototypes (with Rich Mock Data & Motion)

#### Route 1: `/` — Gameweek Telemetry Dashboard
* **Hero Banner**:
  - Title: "PREMIER LEAGUE // GAMEWEEK 28" in `Clash Display` uppercase.
  - Quick Stat Pills: Total Fixtures (10), Avg Model Confidence (64.2%), Biggest Divergence match (Man City vs Liverpool: 8.4% model delta).
* **Interactive Filter Ribbon**:
  - Search input with team autocomplete.
  - Quick toggle pills: `All Matches (10)`, `Top 6 Clashes (2)`, `High Divergence (3)`.
* **Fixture Cards Grid (2-Column Responsive)**:
  - Animated card entrance using `motion.div` with staggered fade-and-slide:
    `initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}`.
  - Each Fixture Card features:
    - Top bar: Gameweek badge, kickoff date/time, and a "Divergence Tag" (`Mild 2.1%` in slate, or `High Divergence 8.4%` in glowing amber).
    - Matchup Header: Bold club names with custom colored monogram badges (e.g. Arsenal red, Chelsea blue) and subtle pitch background graphic.
    - **Dual-Model Split Bars**:
      - **Row 1 — Dixon-Coles**:
        Cyan badge `[DC · Poisson]`. 3-segment bar with smooth animated widths:
        Home 48.2% (Emerald) | Draw 26.1% (Slate) | Away 25.7% (Amber).
      - **Row 2 — XGBoost**:
        Violet badge `[XGB · Trees]`. 3-segment bar:
        Home 54.0% (Emerald) | Draw 23.5% (Slate) | Away 22.5% (Amber).
      - Under the bars, display a subtle mini-diff tag: "XGBoost favors Arsenal by +5.8% over Dixon-Coles".
    - Bottom Action:
      - "Launch Matchup Lab →" button that deep-links to `/simulator?home=Arsenal&away=Chelsea` with hover glow.

---

#### Route 2: `/simulator` — Head-to-Head Tactical Matchup Lab
* **Club Selector Command Center**:
  - Two large selector capsules (Home Club vs Away Club) with team logos/colors.
  - Center swap button (`⇄`) with spring animation:
    `whileTap={{ rotate: 180, scale: 0.9 }} whileHover={{ scale: 1.1 }}`.
* **Strict Side-by-Side Dual-Model Architecture**:
  *(Never render an unvalidated arithmetic average or merged prediction).*
  - **Left Wing: Dixon-Coles Poisson Engine (Cyan Accent Glow)**
    - Header: `GENERATIVE BIVARIATE POISSON` with cyan radar pulse indicator.
    - W/D/L Outcome Pills: Home 48.2% | Draw 26.1% | Away 25.7%.
    - Most Likely Score Badge: Large highlighted capsule `2 – 1` with probability `11.4%` (Implied odds: 8.77).
    - **Interactive 5x5 Poisson Score Probability Heatmap**:
      - 5x5 grid (Home goals 0..4+ on Y-axis, Away goals 0..4+ on X-axis).
      - **Mathematical Luminance Scale**:
        $$s_{ij} = \sqrt{\frac{p_{ij}}{p_{\max}}}, \quad \alpha_{ij} = 0.08 + 0.82 \cdot s_{ij} \in [0.08, 0.90]$$
        $$\text{backgroundColor} = \text{rgba}(0, 242, 254, \alpha_{ij})$$
      - **Motion & Micro-interactions**:
        - Each cell is a `motion.div` with `whileHover={{ scale: 1.12, zIndex: 20 }}` and spring transition `{ type: "spring", stiffness: 400, damping: 25 }`.
        - Draw diagonal (0-0, 1-1, 2-2, etc.) outlined with subtle dashed border.
        - Peak score (2-1) features an animated breathing gold border glow.
        - Tooltip on hover/focus: `Arsenal 2 – 1 Chelsea // 11.4% Probability // Odds 8.77`.
  - **Right Wing: XGBoost ML Engine (Ultraviolet Accent Glow)**
    - Header: `DISCRIMINATIVE GRADIENT BOOSTED TREES` with violet matrix indicator.
    - W/D/L Outcome Pills: Home 54.0% | Draw 23.5% | Away 22.5%.
    - **Tactical Feature Differential HUD**:
      - Visual gauge bars for:
        - `Elo Rating Delta`: `+85 pts` (Home advantage highlighted in green)
        - `Rolling Form (Last 5)`: `13 pts vs 8 pts` (Visual form momentum meter)
        - `Shots on Target / Match`: `5.8 vs 3.4` (Horizontal comparison bar)
        - `Rest Days Gap`: `+2 days fatigue buffer`
    - "Why Models Differ": Contextual callout explaining XGBoost's heavier weight on recent rolling shots-on-target form vs Dixon-Coles' multi-season Poisson decay.

---

#### Route 3: `/teams` & `/teams/[team]` — Club Intelligence Dossier
* **Directory (`/teams`)**:
  - **League-Wide Tactical Scatter Matrix**:
    - X-axis: Attack Strength ($\alpha$, scale 0.6 to 1.8, League Average = 1.00).
    - Y-axis: Defense Conceded ($\beta$, inverted so lower/better defense is at top).
    - Four quadrants with ambient color fills:
      - Top-Right: `ELITE CONTENDERS` (Arsenal, Man City, Liverpool)
      - Bottom-Right: `HIGH-SCORING CHAOS` (Spurs, Brighton)
      - Top-Left: `TACTICAL FORTRESSES` (Everton, Forest)
      - Bottom-Left: `RELEGATION ZONE HAZARD` (Ipswich, Southampton)
    - Interactive dots for all 20 clubs with hover card showing exact $(\alpha, \beta)$ and Elo.
  - Team Cards Grid: 20 clubs with club crest color strip, attack rank, defense rank, and current Elo.
* **Club Deep-Dive (`/teams/[team]`)**:
  - Club Header: Crest, full canonical name, and quick-launch button: `Simulate Next Match →`.
  - Telemetry Gauges:
    - Attack Strength $\alpha = 1.28$ (Above league benchmark $\mu=1.00$)
    - Defense Conceded $\beta = 0.84$ (Stronger than league benchmark)
    - Elo Trajectory: Sparkline trend over last 10 gameweeks.
  - Transparent Staleness Badge:
    `[Live fold active · Evaluated 2026-09-13]` (or `[Stats as of 2026-09-06 · Retraining Pending]`).

---

#### Route 4: `/models` — Statistical Observatory & Evaluation
* **Honest Research Snapshot Banner**:
  > *"Out-of-sample walk-forward benchmark evaluated over 2023–24, 2024–25, and 2025–26 test folds. Historical research snapshot last evaluated: 2026-09-13."*
* **Benchmark Performance Matrix**:
  - Metric Columns: `Model`, `Paradigm`, `RPS (Ranked Probability Score) ↓`, `Brier Score ↓`, `Log-Loss ↓`.
  - Highlight rows:
    - `Dixon-Coles`: `RPS: 0.1984` | `Brier: 0.582` | `Log-loss: 0.984`
    - `XGBoost`: `RPS: 0.1972` | `Brier: 0.579` | `Log-loss: 0.978`
    - `Bookmaker Implied Odds`: `RPS: 0.1945` | `Brier: 0.569` | `Log-loss: 0.962` (Gold benchmark border)
    - `Always Home`: `RPS: 0.2450` | `Brier: 0.710` | `Log-loss: 1.250` (Muted red)
* **Interactive Reliability Diagram (Calibration Curve)**:
  - 10-bin calibration curve with ideal $y=x$ dashed line, Dixon-Coles cyan trajectory, and XGBoost violet trajectory.
  - Hovering any bin shows predicted vs observed frequency.
* **Live Serving Pipeline Telemetry Card**:
  - Status: `Healthy (Postgres connected)`
  - Active Hash: `sha256:5a14114`
  - Hot-Reload Engine: `30s TTL DB Polling · Atomic Pointer Swap`

---

Please generate this prototype with interactive state: tabs switch smoothly between the 4 views using `motion` layout transitions, team selection in the simulator updates the heatmap and feature cards dynamically, and hovering cells/charts triggers responsive spring tooltips.
```

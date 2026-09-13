# MatchSense — Vercel v0 Prototype Brief

> **Purpose**: Standalone, copy-pasteable design brief for Vercel v0.  
> **Source**: Extracted from [`docs/superpowers/specs/2026-09-13-frontend-dashboard-design.md`](file:///d:/Yash%20Kokane/Projects/MatchSense/docs/superpowers/specs/2026-09-13-frontend-dashboard-design.md) (Sections 5 & 6).  
> **Scope**: Front-of-the-frontend UI prototype using static/mock data to validate visual ergonomics, card hierarchy, typography, dark-mode styling, and bespoke chart visualizations.  
> **Target**: Vercel v0 (Next.js / React, Tailwind CSS, Lucide icons, Radix UI primitives).  

---

## v0 Prompt (Copy & Paste Below)

```markdown
You are building the UI prototype for "MatchSense", a premier sports analytics web application that visualizes dual-model Premier League match predictions: a generative statistical model (Dixon-Coles bivariate Poisson) and a discriminative machine learning model (XGBoost).

This is a front-of-the-frontend UI prototype using static mock data to validate visual ergonomics, card hierarchy, typography, dark-mode styling, and bespoke chart visualizations.

---

### 1. Global Visual Design System & Color Tokens

MatchSense uses a dark sports-analytics theme with high contrast, translucent glassmorphic surfaces, and tabular numbers:

* **Backgrounds & Surfaces**:
  - Root Page Background: Deep Obsidian (`#0A0D14`)
  - Elevated Card Background: `rgba(17, 22, 34, 0.75)` with `backdrop-filter: blur(12px)` and border `1px solid rgba(255, 255, 255, 0.08)`
  - Sub-cards / Input Surfaces: `#111622` or `#1A2234`
* **Model Identity Accents (Strict Separation)**:
  - **Dixon-Coles**: Electric Sky Blue (`#0EA5E9` / `#38BDF8` — Hue ~199°)
  - **XGBoost**: Deep Violet (`#8B5CF6` / `#A855F7` — Hue ~270°)
* **Match Outcome Segments (Probabilities)**:
  - **Home Win**: Pure Emerald Green (`#10B981` — Hue ~155°)
  - **Draw**: Slate Gray (`#64748B` — Neutral)
  - **Away Win**: Sunset Amber (`#F59E0B` — Hue ~38°)
  *(Rule: Model identity Sky Blue/Violet must never collide with match outcome Emerald/Slate/Amber).*
* **Typography**:
  - Headings / UI labels: Clean modern sans-serif (`Inter`)
  - All percentages, odds, and metrics: Tabular monospace font (`font-mono tabular-nums tracking-tight`) to ensure stable rendering during transitions.

---

### 2. Global Shell & Navigation
* **Navbar**:
  - Left: "MatchSense" logo with an electric cyan indicator dot.
  - Center: Nav links with active state indicators:
    - `Fixtures` (`/`)
    - `H2H Simulator` (`/simulator`)
    - `Teams` (`/teams`)
    - `Evaluation & Models` (`/models`)
  - Right: System status pill badge:
    `● Models Live` (pill with pulsing emerald dot, dark emerald glass border).

---

### 3. Four Dedicated Route Prototypes (with Mock Data)

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                         Root Layout                             │
  │    [MatchSense Logo]   [Fixtures] [Simulator] [Teams] [Models]   │
  │                        [● Models Live Badge]                   │
  └─────────────────────────────────────────────────────────────────┘
           │                   │                 │              │
           ▼                   ▼                 ▼              ▼
     Route 1: `/`     Route 2: `/simulator` Route 3: `/teams` Route 4: `/models`
  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
  │ Gameweek Hero   │ │ Matchup Combos  │ │ Attack vs   │ │ Architecture Exp │
  │                 │ │ (Home vs Away)  │ │ Defense     │ │                  │
  │ Fixture Cards   │ │                 │ │ Scatter     │ │ Walk-Forward     │
  │ (Dual Model     │ │ Side-by-Side    │ │             │ │ Benchmarks Table │
  │  Split Bars)    │ │ Comparison:     │ │ 20 Clubs    │ │ (Locked Folds)   │
  │                 │ │ • DC Poisson    │ │ Grid        │ │                  │
  │ Deep Dive Links │ │   (5x5 Heatmap) │ │             │ │ Calibration      │
  │ -> /simulator   │ │ • XGBoost       │ │ Club Profile│ │ Curves           │
  │                 │ │   (Feature Diff)│ │ (/teams/[t])│ │ Live Health Card │
  └─────────────────┘ └─────────────────┘ └─────────────┘ └──────────────────┘
```

#### Route 1: `/` — Upcoming Gameweek Forecasts
* **Gameweek Hero**: Displays "Gameweek 28 Forecasts", match countdown pill, and active model versions (`DC v2026.09.13 · XGB v2026.09.13`).
* **Fixture Search/Filter**: Instant client-side text input to filter matches by team name.
* **Fixture Grid (2-column responsive layout)**:
  - Render 4–6 mock Premier League matches (e.g., Arsenal vs Chelsea, Man City vs Liverpool, Spurs vs Newcastle).
  - Each fixture card displays:
    - Kickoff time (e.g., `Sat 19 Sep · 15:00`) and GW badge.
    - Home & Away club names with clean initial badges/colors.
    - **Dual-Model Probability Bars**:
      - Top row: `Dixon-Coles` badge (cyan dot) with 3-segment bar: `Home 48.2%` (Emerald) | `Draw 26.1%` (Slate) | `Away 25.7%` (Amber).
      - Bottom row: `XGBoost` badge (violet dot) with 3-segment bar: `Home 52.0%` (Emerald) | `Draw 24.5%` (Slate) | `Away 23.5%` (Amber).
      - Width of segments strictly matches percentages.
    - Bottom link: "Simulate in H2H →" (deep-links to `/simulator?home=Arsenal&away=Chelsea`).

---

#### Route 2: `/simulator` — Interactive Head-to-Head Simulator
* **Matchup Selectors**:
  - Two comboboxes for Home and Away clubs (defaulting to Arsenal vs Chelsea), with a 1-click swap button (`⇄`).
* **Strict Side-by-Side Architecture Block** (Do NOT render any arithmetic average or consensus bar):
  - **Left Card: Dixon-Coles (Generative · Bivariate Poisson)**
    - Tag: `Generative · Bivariate Poisson` in cyan.
    - Outcome split boxes: Home 48.2%, Draw 26.1%, Away 25.7%.
    - Predicted score badge: `Most Likely Score: 2 – 1 (11.4%)`.
    - **5x5 Poisson Score Probability Heatmap**:
      - Rows: Home goals (0, 1, 2, 3, 4+). Columns: Away goals (0, 1, 2, 3, 4+).
      - **Mathematical Heatmap Scaling**:
        For cell probability $p_{ij}$ and maximum grid probability $p_{\max}$:
        $$s_{ij} = \sqrt{\frac{p_{ij}}{p_{\max}}} \in [0, 1]$$
        $$\alpha_{ij} = 0.08 + 0.82 \cdot s_{ij} \in [0.08, 0.90]$$
        $$\text{backgroundColor} = \text{rgba}(14, 165, 233, \alpha_{ij}) \quad (\text{Sky Blue})$$
      - **Visual Features**:
        - Draw diagonal cells (0-0, 1-1, 2-2, 3-3, 4-4) have a subtle dashed outline (`border border-dashed border-slate-500/40`).
        - The most likely score cell (e.g. 2-1) has a glowing amber ring (`ring-2 ring-amber-400`).
        - Hovering any cell shows a tooltip: e.g. `Arsenal 2 – 1 Chelsea: 11.4% probability (Implied odds: 8.77)`.
  - **Right Card: XGBoost (Discriminative · Gradient Boosted Trees)**
    - Tag: `Discriminative · Gradient Boosted Trees` in violet.
    - Outcome split boxes: Home 52.0%, Draw 24.5%, Away 23.5%.
    - **Feature Differential Table**:
      - `Elo Differential (Δ Elo)`: `+85 pts`
      - `Rolling Form (Last 5 Pts)`: `13 vs 8`
      - `Shots on Target Diff`: `+2.4 / game`
      - `Rest Days Differential`: `+2 days (fatigue advantage)`

---

#### Route 3: `/teams` & `/teams/[team]` — Club Directory & Profiles
* **Directory (`/teams`)**:
  - **League Strength Scatter Plot**:
    - X-axis: Attack Strength ($\alpha$, range 0.6 to 1.8, benchmark $\mu=1.0$).
    - Y-axis: Defense Rating ($\beta$, range 0.6 to 1.8, inverted so lower/better defense is higher).
    - Quadrant labels: Elite (top-right), High Scoring (bottom-right), Defensive (top-left), Underperforming (bottom-left).
    - Plot dots for PL clubs with hover tooltips showing $(\alpha, \beta)$.
  - Responsive grid of team cards showing club name, attack rank, defense rank, and current Elo.
* **Club Deep-Dive (`/teams/[team]`)**:
  - Club header with badge and "Simulate in H2H →" button.
  - Strength gauges:
    - Attack Strength $\alpha = 1.28$ (Above league average $\mu=1.0$)
    - Defense Conceded $\beta = 0.84$ (Better than league average $\mu=1.0$)
    - Elo Rating: `1845`
  - Rolling Stats Card: Form points (last 5 matches), shots on target per match (5.8), corners per match (6.2).
  - Transparent staleness indicator badge:
    `[Live fold active · Evaluated 2026-09-13]` (or `[Stats as of 2026-09-06 · Retraining Pending]`).

---

#### Route 4: `/models` — Walk-Forward Benchmarks & Architecture Showcase
* **Honest Research Snapshot Banner**:
  > *"Out-of-sample walk-forward benchmark evaluated over 2023–24, 2024–25, and 2025–26 test folds. Historical research snapshot last evaluated: 2026-09-13."*
* **Benchmark Comparison Table**:
  - Columns: `Model Architecture`, `Paradigm`, `Ranked Prob Score (RPS) ↓`, `Brier Score ↓`, `Log-Loss ↓`.
  - Rows:
    - `Dixon-Coles` (Generative Poisson, $\xi=0.005$, $\rho$): `RPS: 0.1984` | `Brier: 0.582` | `Log-loss: 0.984`
    - `XGBoost` (Discriminative Trees, Elo, Form): `RPS: 0.1972` | `Brier: 0.579` | `Log-loss: 0.978`
    - `Bookmaker Odds` (Market Baseline): `RPS: 0.1945` | `Brier: 0.569` | `Log-loss: 0.962`
    - `Always Home` (Naive Baseline): `RPS: 0.2450` | `Brier: 0.710` | `Log-loss: 1.250`
* **Calibration Curves (Reliability Diagram)**:
  - 10-bin line chart comparing predicted probability against observed empirical frequency.
  - Dashed diagonal line for ideal $y=x$ calibration.
  - Dixon-Coles cyan line and XGBoost violet line tracking close to the ideal diagonal.
* **Live Serving Pipeline Status Card**:
  - Displays: DB connectivity status, hot-reload method (atomic pointer swap), and reload cadence (30s TTL DB polling).

---

Please generate this prototype with interactive state (tab switching between the 4 routes, team combobox selection in the simulator updating the score heatmap and feature cards, and tooltips on the heatmap cells).
```

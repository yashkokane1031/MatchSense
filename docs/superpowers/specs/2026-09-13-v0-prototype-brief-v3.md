# MatchSense V3 — Bento Dashboard Prototype Brief

> **Source**: User-provided reference design ("Sportify" dark dashboard).  
> **Layout Model**: Left Sidebar Navigation + Top Header + Multi-Card Bento Grid.  
> **Style**: Deep midnight slate, soft purple/indigo active pills, rounded cards (`rounded-2xl`), clean horizontal comparative bars, zero neon clutter.  
> **Target**: Copy-pasteable into Vercel v0 with interactive mock data.

---

## What Changes in V3 (Direct Match with Reference Design)

1. **Left Sidebar Navigation**: Replaces top-only navbar with a permanent, sleek dark sidebar (`Dashboard`, `Fixtures`, `H2H Simulator`, `Team Rankings`, `Model Observatory`, `Settings`), featuring active purple pills (`bg-indigo-600/90 text-white rounded-xl`).
2. **Featured Match Centerpiece**: A large, rounded hero match card displaying the marquee fixture (e.g. Man City vs. Liverpool), prominent club crests, predicted score (`2 - 1`), stadium, and kickoff time.
3. **Horizontal Comparative Telemetry Bars**: Exactly like the reference "Match Stats" card, comparative horizontal bars (Indigo for Home, Coral/Pink for Away) showing Elo, Attack $\alpha$, Defense $\beta$, Rolling Form, and Model Probabilities.
4. **Bento Card Structure**:
   - Top-right Model Divergence Spotlight card.
   - Middle row: "Team Strength Leaders" (attack $\alpha$ pills) + "League Standings & Ratings" table.
   - Right column: "Upcoming Fixtures" mini-feed with club badges, kickoff time, and "View All" button.
5. **Calm, High-End Color Palette**:
   - Deep obsidian background (`#0B0E17`).
   - Cards: Soft slate-charcoal (`#151A28`) with faint borders (`border-white/5`).
   - Accents: Soft Indigo (`#6366F1`) + Coral Rose (`#F43F5E`) + Slate (`#64748B`). Zero loud neon green bloom.

---

## v0 Copy-Paste Prompt (V3)

```markdown
Build a sleek, modern Premier League football analytics dashboard prototype called "MatchSense" in dark mode. 

The design must strictly follow this visual and structural blueprint:
- A fixed left sidebar for navigation with rounded active pills.
- A top bar with a search input, notifications, and user avatar.
- A responsive multi-card "Bento Grid" dashboard layout.
- Deep midnight navy background, soft rounded card surfaces, clean horizontal comparison bars, and soft purple/indigo accents (zero harsh neon glows).

---

### 1. Color System & Surfaces
* **Canvas Background**: Deep Midnight Charcoal (`#0B0E17` or `#0E121E`).
* **Card Surfaces**: Soft Dark Navy (`#151A28` / `#161C2C`), `rounded-2xl` (~16px radius), with subtle border `1px solid rgba(255, 255, 255, 0.06)`.
* **Primary Accent (Active / Home)**: Royal Indigo / Purple (`#6366F1` / `#5856D6`).
* **Secondary Accent (Away / Opposition)**: Coral / Rose Red (`#F43F5E` / `#E11D48`).
* **Text**: Crisp white titles (`#FFFFFF`), muted slate subtitles and labels (`#94A3B8`).

---

### 2. Left Sidebar Navigation
* **Brand**: `MatchSense` with a clean geometric football/shield logo icon in indigo.
* **Menu Items** (vertical stack with clean icons):
  - `Dashboard` (active by default with a solid purple pill: `bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 rounded-xl px-4 py-3 flex items-center gap-3`)
  - `Fixtures` (calendar icon)
  - `H2H Simulator` (split/swords icon)
  - `Team Rankings` (shield icon)
  - `Model Observatory` (chart icon)
  - `Settings` (gear icon)
* **Bottom Sidebar Card**:
  - A compact rounded card (`bg-[#101422] p-3.5 rounded-xl border border-white/5`):
  - Heading: "Serving Engine"
  - Subtext: "30s hot-reload active · DB healthy"
  - Button: "Model Docs" (`bg-indigo-600/80 hover:bg-indigo-600 text-xs py-1.5 rounded-lg text-white font-medium`)

---

### 3. Top Header Bar
* Left: Personalized greeting / status: **"Good evening, Alex 👋"** or **"Premier League // Gameweek 28"**.
* Right:
  - Search pill input with magnifying glass: `"Search teams, matches, metrics..."` (`bg-[#151A28] rounded-full border border-white/10 text-xs px-4 py-2 w-64`).
  - Notification bell with a red badge pill `(3)`.
  - Rounded user avatar image / profile circle.

---

### 4. Bento Grid Dashboard Layout (Main View)

```
┌─────────────────────────────────────────────────────────────┬──────────────────────────┐
│  FEATURED MATCH (Hero Card)                                 │  MODEL SPOTLIGHT         │
│  [Premier League]                           [Upcoming 15:00]│  [Divergence Focus]      │
│  (Crest) Man City       2 – 1       Liverpool (Crest)       │  Dixon-Coles vs XGBoost  │
│  Etihad Stadium                                             │  [Explore Matchup]       │
│  Expected: Haaland 0.82 xG · Salah 0.61 xG                  │                          │
├──────────────────────────────┬──────────────────────────────┼──────────────────────────┤
│  TEAM STRENGTH LEADERS       │  LEAGUE MODEL STANDINGS      │  UPCOMING FIXTURES       │
│  1. Man City      1.38 [α]   │  Pos Team       Att  Def  Elo│  Arsenal vs Chelsea      │
│  2. Arsenal       1.32 [α]   │  1   Man City  1.38 0.82 1940│  Old Trafford · 20:30    │
│  3. Liverpool     1.28 [α]   │  2   Arsenal   1.32 0.84 1910│  Spurs vs Newcastle      │
│  4. Aston Villa   1.18 [α]   │  3   Liverpool 1.28 0.89 1885│  Sun, 19 May             │
├──────────────────────────────┴──────────────────────────────┼──────────────────────────┤
│  MATCH TELEMETRY & COMPARATIVE STATS (Horizontal Bars)      │  LATEST MODEL AUDITS     │
│  Man City                                         Liverpool │  • 2025-26 Fold Verified │
│  62% ═══════════════ Poisson Prob ═════════════ 38%         │  • Zero parameter drift  │
│  1940 ══════════════ Elo Rating   ═════════════ 1885        │  • Next sync: Tue 03:00  │
│  1.38 ══════════════ Attack α     ═════════════ 1.28        │                          │
│  0.82 ══════════════ Defense β    ═════════════ 0.89        │                          │
└─────────────────────────────────────────────────────────────┴──────────────────────────┘
```

#### Detailed Components:

##### A. Featured Match Card (Top Center Hero)
* Gradient dark background (`from-[#1a1c30] to-[#121624]`).
* Top bar: `Premier League` with competition logo, right side shows `Upcoming · Sat 15:00`.
* Center: Large club crests for **Man City** and **Liverpool**.
* Center Scoreline / Forecast: Large bold **`2 – 1`** with stadium name (`Etihad Stadium`) below it.
* Below: Goal forecast tags (e.g., `Haaland 68% score prob` · `Salah 44% score prob`).

##### B. Match Telemetry & Comparative Stats (Bottom Center)
* Exactly like the reference "Match Stats" card:
* Club names on left and right: **Man City** (Indigo) vs **Liverpool** (Coral Red).
* 4–5 horizontal split comparison bars:
  - **Poisson Win Prob**: Home 54% (Indigo bar) vs Away 24% (Coral bar) [Draw 22% in center]
  - **Elo Rating**: 1940 vs 1885
  - **Attack Strength (α)**: 1.38 vs 1.28
  - **Defense Conceded (β)**: 0.82 vs 0.89 (lower is better)
  - **Recent Form (Last 5)**: 13 pts vs 10 pts

##### C. Team Strength Leaders Card (Middle Left)
* Header: `Strength Leaders` with `View All` link.
* List of top 4 clubs with avatar/crest, name, position/rating:
  - 1. Man City — Attack $\alpha$ `1.38` (in purple pill)
  - 2. Arsenal — Attack $\alpha$ `1.32` (in purple pill)
  - 3. Liverpool — Attack $\alpha$ `1.28` (in purple pill)
  - 4. Aston Villa — Attack $\alpha$ `1.18` (in purple pill)

##### D. League Model Standings Table (Middle Center)
* Header: `Model Standings` with `View All` link.
* Table columns: `Pos`, `Team`, `Attack α`, `Defense β`, `Elo`.
* Sleek rows with club crest, clean tabular numbers.

##### E. Upcoming Fixtures Mini-Feed (Middle Right)
* Header: `Upcoming Fixtures` with `View All` link.
* Mini match card:
  - League tag: `Premier League` · `Sun, 19 May`
  - Two club badges with `VS` in center: **Man Utd** vs **Chelsea**
  - Venue & kickoff: `Old Trafford · 8:30 PM`

##### F. Model Spotlight Card (Top Right)
* A high-contrast purple/blue card with a subtle gradient background:
* Title: **Dual-Model Divergence**
* Text: *"Dixon-Coles and XGBoost show 8.4% delta on Arsenal vs Chelsea."*
* Button: `"Launch H2H Simulator"` (`bg-indigo-600 hover:bg-indigo-500 rounded-xl px-4 py-2 text-xs font-semibold text-white`).

---

### 5. Other Route Views (When Clicking Sidebar)
* **`H2H Simulator` View**:
  - The hero card expands into the interactive match simulator with team selectors, the 5x5 Poisson score probability matrix (hoverable cells), and XGBoost feature breakdowns.
* **`Fixtures` View**:
  - Bento grid switches to a clean 2-column or 3-column card grid of all 10 gameweek fixtures with dual-model probability bars.
* **`Model Observatory` View**:
  - Walk-forward benchmark tables (2023–24, 2024–25, 2025–26 folds) and calibration curves styled in matching dark bento cards.

Ensure smooth interactivity (switching tabs in sidebar swaps the active view, clicking a match updates the featured comparison).
```

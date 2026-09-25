# 🚀 MatchSense Production Deployment Guide (100% Free Tier)

This guide walks you through deploying MatchSense with zero hosting costs, automated weekly model retraining, and zero-downtime prediction updates.

---

## 🏗️ Architecture Overview

```
                                      ┌────────────────────────────────────────────────────────┐
                                      │                    GitHub Actions                      │
                                      │  (Weekly Retraining Cron: Tuesday 03:00 UTC)           │
                                      │                                                        │
                                      │  1. Ingests weekend match results                      │
                                      │  2. Retrains Dixon-Coles & XGBoost                     │
                                      │  3. Validates Gate 2A Invariants                       │
                                      │  4. Commits new model artifacts & precomputes preds    │
                                      └──────────────────────────┬─────────────────────────────┘
                                                                 │
                                                                 ▼
┌─────────────────────────┐          ┌─────────────────────────────────────────────────────────┐
│     Next.js Frontend    │          │               Neon Serverless PostgreSQL                │
│    (Hosted on Vercel)   │          │                     (Free 0.5 GB)                       │
│                         │          │                                                         │
│   • Upcoming Fixtures   │          │   • matches table (Historical results)                  │
│   • H2H Simulator       │          │   • fixtures table (Precomputed predictions via JSONB)  │
│   • Model Benchmarks    │          │   • model_artifacts table (Versioned model blobs)       │
│   • Team Profiles       │          └──────────────────────────▲──────────────────────────────┘
└───────────┬─────────────┘                                     │
            │                                                   │ Queries / Hot-reloads
            │ HTTP REST Requests                                │
            ▼                                                   │
┌───────────────────────────────────────────────────────────────┴──────────────────────────────┐
│                                FastAPI Prediction Service                                    │
│                              (Hosted on Render - Free Tier)                                  │
│                                                                                              │
│   • ModelManager (In-memory serving + background DB polling)                                 │
│   • Zero-downtime dynamic hot-reload when new artifacts arrive                               │
│   • REST API endpoints (/api/v1/health, /fixtures/upcoming, /predictions/compare)           │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Create Free PostgreSQL Database (Neon)

1. Navigate to [neon.tech](https://neon.tech) and sign up for a free account (no credit card required).
2. Click **Create Project**, name it `matchsense`, and choose a region close to you or your users (e.g. `US East (Ohio)` or `EU (Frankfurt)`).
3. In the project dashboard, copy the **Connection string**:
   ```text
   postgresql://[user]:[password]@[endpoint].neon.tech/neondb?sslmode=require
   ```
   *(Keep this string handy for Steps 2 and 3).*

---

## Step 2: Configure GitHub Secrets & Run Initial Population

1. In your GitHub repository (`yashkokane1031/MatchSense`), navigate to:
   **Settings** → **Secrets and variables** → **Actions** → Click **New repository secret**.
2. Add the following two secrets:
   * **`DATABASE_URL`**: Your Neon connection string from Step 1.
   * **`FOOTBALL_DATA_API_KEY`**: `9560bd6247584571b946aa48f9cb4377`
3. Trigger the initial database provisioning and model training:
   * Go to the **Actions** tab in GitHub.
   * Click **Weekly Pipeline Sync** in the left sidebar.
   * Click **Run workflow** → select branch `master` → Click the green **Run workflow** button.
   * *This automatically applies Alembic migrations, creates all database tables, ingests historical data and live fixtures, fits both models, and saves the first production checkpoints to your cloud database.*

---

## Step 3: Deploy FastAPI Backend on Render (Free)

1. Sign up or log into [render.com](https://render.com) using your GitHub account.
2. In the Render Dashboard, click **New +** → select **Web Service**.
3. Select your `MatchSense` repository.
4. Render will detect `render.yaml` or Docker:
   * **Name**: `matchsense-api`
   * **Runtime**: `Docker` (Render automatically uses our root [Dockerfile](file:///d:/Yash/Kokane/Projects/MatchSense/Dockerfile))
   * **Instance Type**: Select **Free**
5. Under **Environment Variables**, add:
   * `DATABASE_URL`: *(Your Neon connection string from Step 1)*
   * `FOOTBALL_DATA_API_KEY`: `9560bd6247584571b946aa48f9cb4377`
   * `LOG_LEVEL`: `INFO`
6. Click **Create Web Service**.
7. Once deployed, Render will provide a free public URL:
   ```text
   https://matchsense-api.onrender.com
   ```
   *Verify it by visiting `https://matchsense-api.onrender.com/api/v1/health` in your browser. You should see `"status": "healthy"`, `"database_connected": true`, and model metadata.*

---

## Step 4: Deploy Next.js Frontend on Vercel (Free)

1. Sign up or log into [vercel.com](https://vercel.com) using your GitHub account.
2. Click **Add New...** → **Project** → Import `yashkokane1031/MatchSense`.
3. In the project configuration:
   * **Framework Preset**: `Next.js`
   * **Root Directory**: Click **Edit** and set it to `frontend`
4. Expand **Environment Variables** and add:
   * **`NEXT_PUBLIC_API_URL`**: `https://matchsense-api.onrender.com/api/v1` *(your Render backend URL from Step 3 with `/api/v1` appended)*
5. Click **Deploy**.
6. Vercel will build and launch your dashboard at:
   ```text
   https://matchsense.vercel.app
   ```

---

## 🔄 How Automated Weekly Syncing Works

* Every **Tuesday at 03:00 UTC** (configured in [.github/workflows/weekly_sync.yml](file:///d:/Yash/Kokane/Projects/MatchSense/.github/workflows/weekly_sync.yml)):
  1. GitHub Actions wakes up.
  2. Fetches newly completed fixtures from Football-Data.org.
  3. Re-trains the Dixon-Coles Poisson model (with Two-Pass Bayesian Shrinkage) and the XGBoost tree booster.
  4. Runs Gate 2A validation tests.
  5. Updates `model_artifacts` and upcoming fixture predictions in Neon PostgreSQL.
  6. The running Render backend detects the new model timestamp via `ModelManager` and swaps the models in-memory with zero downtime.
  7. Your Vercel frontend automatically reflects the latest probabilities and scoreline heatmaps.

---

## 💡 Free-Tier Tips & Behaviors

* **Render Cold Starts**: Render's free tier spins down the backend container after 15 minutes of inactivity. When you visit the Vercel site after a period of dormancy, the first request will take ~20–30 seconds for the backend to wake up. The frontend health badge will indicate "API Offline" during the spin-up and automatically switch to "Models Live" once the container responds.
* **Database Storage**: The entire Premier League dataset (all historical seasons + current season) consumes less than 40 MB, well within Neon's 500 MB free allowance.
* **GitHub Actions Usage**: The weekly synchronization takes approximately 45 seconds to complete. Running 4 times a month consumes ~3 minutes of GitHub Actions out of your 2,000 free minutes per month.

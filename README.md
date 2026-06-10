# Building Permit Dashboard

A multi-page [Streamlit](https://streamlit.io/) application that visualizes annual and
monthly building-permit data for the 11-county Atlanta metro region, sourced from the
U.S. Census Bureau's Building Permits Survey (BPS).

The live app is hosted on **Heroku** and auto-deploys from this repository: any commit
pushed to the `main` branch triggers a rebuild and redeploy.

---

## Getting started (for maintainers)

> **Prerequisites**
> - **Write access** to this repository. It lives in the `arc-research-analytics`
>   GitHub organization — an org admin must add you as a collaborator before you can push.
> - **Python 3.11** (the version this app is built and deployed against).

You have two ways to work on the app. Codespaces needs no local setup; the local path
gives you a normal editor + terminal on your own machine.

### Option A — GitHub Codespaces (no local setup)

1. On the repo's GitHub page, click **Code → Codespaces → Create codespace on main**.
2. The included [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) builds
   a Python 3.11 container, installs `requirements.txt`, and launches the app
   automatically (forwarded on port 8501 — a preview opens on its own).
3. Edit files in the browser-based VS Code, then commit and push (see **Making changes**).

### Option B — Local development

```bash
# 1. Clone over HTTPS (works for everyone; no special SSH config needed)
git clone https://github.com/arc-research-analytics/hud_permit_viz.git
cd hud_permit_viz

# 2. Create an isolated Python 3.11 environment, then install dependencies.
#    Using venv:
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

#    ...or using conda:
#    conda create -n permit_viz python=3.11 -y
#    conda activate permit_viz
#    pip install -r requirements.txt

# 3. Run the app locally (opens at http://localhost:8501)
streamlit run main.py
```

### Making changes and deploying

1. Create a branch, make your edits, and test locally (`streamlit run main.py`).
2. Open a pull request into `main` (or commit to `main` directly if that's your team's
   workflow).
3. **Once changes land on `main`, Heroku auto-deploys them** — no manual deploy step.
   Give it a couple of minutes, then check the live URL.

---

## Project layout

| Path | What it is |
|---|---|
| [main.py](main.py) | App entry point — page registration, navigation, global CSS. |
| [utils.py](utils.py) | Shared helpers (county color map, provisional-data captions, widget callbacks). |
| [views/](views/) | The five dashboard pages (Overview, Compare, Annual Trends, Monthly Trends, About). |
| [Data/](Data/) | The four dashboard CSVs the app reads. `Data/raw/` holds the fetched source masters. |
| [backend/](backend/) | The data-refresh pipeline (see below). |
| [.github/workflows/refresh-data.yml](.github/workflows/refresh-data.yml) | Scheduled GitHub Action that refreshes the data. |
| [.streamlit/config.toml](.streamlit/config.toml) | Theme (colors, fonts). |
| [assets/](assets/) | Logo images. |
| `Procfile`, `setup.sh` | Heroku startup configuration. |
| [.devcontainer/](.devcontainer/) | Codespaces / dev-container definition. |

---

## Automated data refresh

Data is refreshed automatically by the **Refresh permit data** GitHub Actions workflow
([.github/workflows/refresh-data.yml](.github/workflows/refresh-data.yml)). **No manual
data pull is required** — the old external script is no longer used.

**Schedule:** the workflow runs twice a month — on the **19th** and **26th** at
**14:00 UTC** (`cron: 0 14 19,26 * *`). Two runs absorb any slippage in the Census
publication date (BPS revised-monthly data typically posts mid-month); the runs are
idempotent, so a run that finds no new data simply commits nothing.

Each run fetches **both** datasets:

- **Monthly** revised-monthly permit data (rolling 18-month window).
- **Annual** benchmarked permit data (rolling 3-year window). Because the annual files
  are fetched on every run, the benchmarked annual totals that BPS releases each **May**
  are picked up automatically on the first run after they post — no separate schedule needed.

You can also trigger a run on demand from the repo's **Actions** tab: select
**Refresh permit data → Run workflow** (`workflow_dispatch`).

### What happens in a run

1. [backend/fetch_permits.py](backend/fetch_permits.py) pulls from public Census endpoints
   (no API key needed) → writes the raw masters to `Data/raw/` (`BPS_GA.csv`,
   `BPS_GA_annual.csv`).
2. [backend/backend_query.py](backend/backend_query.py) rebuilds the four dashboard CSVs
   in `Data/`. Deep annual history (1980–) is preserved in-repo across runs.
3. Changed `Data/**/*.csv` files are committed back to `main`, which triggers the Heroku
   auto-deploy so the live app updates.

> The pipeline's own dependencies are pinned separately in
> [backend/requirements-pipeline.txt](backend/requirements-pipeline.txt) (just `pandas` +
> `python-dateutil`) to keep the Action fast. The app's runtime dependencies are in the
> root [requirements.txt](requirements.txt).

### Note on "Dependency Graph" in the Actions tab

If you see a workflow named **Dependency Graph** alongside **Refresh permit data**, that
one is managed by GitHub itself (it scans the `requirements.txt` files for the dependency
graph / security alerts). It runs automatically and **never needs to be run manually** —
it has no effect on the data or the app.

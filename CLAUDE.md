# Building Permit Tracker — Claude Code guide

## Running the app locally

```bash
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate streamlit_dev
streamlit run main.py
```

Opens at http://localhost:8501. Use `streamlit_dev` — not `research`, which lacks Streamlit.

## Running the data pipeline locally

```bash
conda activate research
python backend/fetch_permits.py
python backend/backend_query.py
```

Pipeline dependencies are pinned separately in `backend/requirements-pipeline.txt` (`pandas` + `python-dateutil`). No Census API key is required — all endpoints are public.

## Project layout

| Path | What it is |
|---|---|
| `main.py` | Entry point — page registration, navigation, global CSS. |
| `utils.py` | Shared helpers: county color map, provisional-data captions, widget callbacks. |
| `views/` | Five dashboard pages (Overview, Compare, Annual Trends, Monthly Trends, About). |
| `Data/` | Dashboard CSVs the app reads at runtime. `Data/raw/` holds fetched source masters (gitignored). |
| `backend/fetch_permits.py` | Pulls monthly and annual BPS data from Census → `Data/raw/`. |
| `backend/backend_query.py` | Rebuilds the four dashboard CSVs in `Data/` from the raw masters. |
| `.github/workflows/refresh-data.yml` | Scheduled GitHub Action (19th & 26th, 14:00 UTC). Posts a Teams card on completion. |
| `teams-notification.md` | Reference doc explaining how Teams notifications are wired up. |

## Data & deploy flow

1. GitHub Actions runs `fetch_permits.py` → `backend_query.py` on the 19th and 26th of each month.
2. Changed `Data/**/*.csv` files are committed back to `main` via `git-auto-commit-action`.
3. Heroku auto-deploys on any push to `main` — no manual deploy step needed.
4. A Teams Adaptive Card (success or failure) is posted to the pipeline notifications channel after every run via the `TEAMS_WEBHOOK_URL` repo secret.

Runs are idempotent: if Census has no new data, nothing is committed and Heroku does not redeploy.

## Key invariants — don't break these

- **`Data/raw/` is gitignored.** Raw Census masters exist only during a pipeline run and are never committed.
- **Annual history before the 3-year rolling window is preserved.** `backend_query.py` merges new window rows with the pre-window rows already in the CSVs. Never overwrite the CSVs from scratch.
- **`backend/` code is not imported by the app.** The `Data/*.csv` files are the only contract between the pipeline and the dashboard.
- **Provisional annual rows** (summed from monthlies when a benchmarked BPS annual file isn't yet published) are flagged with `provisional=True`; `utils.provisional_caption()` surfaces this to users in the UI.

## Secrets

| Secret | Where used |
|---|---|
| `TEAMS_WEBHOOK_URL` | `refresh-data.yml` — posts pipeline success/failure cards to the Teams channel. |

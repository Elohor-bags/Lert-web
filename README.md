# !LERT (`alert-intel`) — Pitch Console, Stripe Billing & Full-Stack Starter

This archive contains the complete interactive **!LERT** pitch console and live triage/Stripe demo (`index.html`), plus a starter FastAPI + Stripe backend (`backend/app/main.py`) and Render blueprint (`render.yaml`).

## Quick Host on GitHub Pages
1. Extract the zip file into your repository root.
2. Push to `main`:
   ```bash
   git add .
   git commit -m "Add !LERT pitch console, Stripe checkout demo, and FastAPI starter"
   git push -u origin main
   ```
3. In GitHub repository **Settings → Pages**, set **Source** to **Deploy from a branch** (`main` / `/ (root)`).

## Run FastAPI Backend Locally or on Render
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

# Next.js migration

This migration keeps the existing Streamlit app intact and adds a new frontend
in `next-frontend/` plus a lightweight FastAPI bridge in `api_server.py`.

## Run the API

```bash
.venv/bin/python -m uvicorn api_server:app --reload --port 8000
```

## Run the Next.js frontend

```bash
cd next-frontend
pnpm install
pnpm dev
```

Then open `http://localhost:3000`.

If your terminal cannot find `node`, use the Codex bundled runtime:

```bash
cd next-frontend
PATH=/Users/yihanliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH \
  /Users/yihanliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm dev
```

## Current coverage

- Template type list reads from `config.py`.
- Template list reads from `TEMPLATE_MASTER_CONFIG`.
- Default copy reads from `DEFAULT_COPY_DATA`.
- Local gallery images are served from `assets/backgrounds`.
- Poster rendering is exposed as `POST /api/poster/render`.

The Streamlit app remains available for the original login, role management,
upload review, and full production workflow while the Next.js UI is completed.

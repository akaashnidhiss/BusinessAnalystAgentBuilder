## MCP Demo Frontend Scaffold

Minimal React outline to pair with the FastAPI backend.

### Pages / Components
- `UploadPage`: file input -> `POST /api/users/{user_id}/datasets/preview`; show `upload_id` and inferred schema.
- `ConfigPage`: let user mark filterable dims vs metrics; `POST /api/users/{user_id}/datasets` to create a dataset and run ETL/taxonomy.
- `EtlPage`: informational; ETL + DuckDB init now happen automatically as part of dataset creation.
- `TaxonomyPreview`: fetch `/api/users/{user_id}/taxonomy`; render YAML routing map in a monospaced panel with copy button.
- `QueryPlayground`: NL intent box (placeholder) + advanced filter chips -> `POST /api/users/{user_id}/run/filters`; show results table and diag (requested vs used filters, returned rows). A separate endpoint `/api/users/{user_id}/run/agent` is available for full agent runs.

### Running locally (mock backend)
1) In another shell: `python -m uvicorn mock_backend:app --reload` (serves http://localhost:8000).
2) In `frontend/`: `npm install` then `npm run dev`.
3) Visit the dev server (default http://localhost:5173). API calls are proxied to http://localhost:8000 by default; override with `VITE_API_BASE`.

### API helpers
- `POST /api/users/{user_id}/datasets/preview` (FormData)
- `POST /api/users/{user_id}/datasets`
- `GET /api/users/{user_id}/datasets`
- `GET /api/users/{user_id}/taxonomy`
- `POST /api/users/{user_id}/run/filters`
- `POST /api/users/{user_id}/run/agent`

### UI notes
- Keep the steps linear (upload -> schema -> taxonomy -> query); ETL is implicit in dataset creation.
- Show the taxonomy YAML prominently so users see the router that constrains the tool.
- Diagnostics should surface the canonical filters and any reasons for backoff or empty results returned by the backend.

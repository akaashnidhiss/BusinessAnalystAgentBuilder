## MCP Demo Frontend Scaffold

Minimal React outline to pair with the FastAPI backend.

### Pages / Components
- `UploadPage`: file input -> `POST /api/datasets/upload`; show `dataset_id`.
- `ConfigPage`: fetch sample columns; let user mark filterable vs retrievable; `POST /api/datasets/{id}/config`.
- `EtlPage`: trigger ETL + DuckDB init via `/etl` then `/duckdb/init`; show stats.
- `TaxonomyPreview`: fetch `/taxonomy`; render YAML string in a monospaced panel with copy button.
- `QueryPlayground`: NL query box (placeholder) + advanced filter chips -> `POST /api/query`; show results table and diag (effective filters, backoff level, returned rows).

### Running locally (mock backend)
1) In another shell: `python -m uvicorn mock_backend:app --reload` (serves http://localhost:8000).
2) In `frontend/`: `npm install` then `npm run dev`.
3) Visit the dev server (default http://localhost:5173). API calls are proxied to http://localhost:8000 by default; override with `VITE_API_BASE`.

### API helpers
- `POST /api/datasets/upload` (FormData)
- `POST /api/datasets/{id}/config`
- `POST /api/datasets/{id}/etl`
- `GET /api/datasets/{id}/taxonomy`
- `POST /api/datasets/{id}/duckdb/init`
- `POST /api/query`

### UI notes
- Keep the steps linear (upload -> config -> etl -> taxonomy -> query).
- Show the taxonomy YAML prominently so users see the router that constrains the tool.
- Diagnostics should surface `backoff_level`, `reason`, and `canonical_filters` returned by the backend.

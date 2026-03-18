# Test Plan: frontend-root-env-loading

## What changed
- Pointed the Vite frontend at the repo root for env loading.
- Documented that frontend `VITE_*` variables are read from the repo root `.env`.

## Acceptance criteria coverage
- AC1: Inspect `frontend/vite.config.js` to confirm `envDir` is set to the repository root.
- AC2: Inspect `frontend/src/lib/api.js` to confirm `import.meta.env.VITE_API_BASE_URL` still takes precedence over the fallback URL.
- AC3: Inspect `README.md` to confirm the quick-start instructions mention that the frontend reads `VITE_*` values from the repo root `.env`.

## Edge cases
- Frontend still starts if the repo root `.env` is missing because the API module keeps its localhost fallback.
- Only `VITE_*` variables are exposed by Vite to client code.

## Notes
- Automated coverage for this change is minimal because the behavior is defined by Vite configuration rather than app logic.
- Validation for this change is primarily configuration and documentation inspection plus a dev-server restart.

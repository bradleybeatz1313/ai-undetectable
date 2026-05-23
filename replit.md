# AI Undetectable

Make AI-generated images undetectable — one API call transforms them to pass detection tests.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port from `PORT` env)
- `pnpm --filter @workspace/ai-undetectable run dev` — run the frontend (port from `PORT` env)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- Required env: `DATABASE_URL` — Postgres connection string (for future use)

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Frontend: React + Vite (Tailwind CSS, wouter routing)
- API: Express 5 with Sharp for image processing
- DB: PostgreSQL + Drizzle ORM (scaffolded, not yet used)
- Build: esbuild (CJS bundle for API server)

## Where things live

- `artifacts/ai-undetectable/` — React/Vite landing page (ported from original HTML)
  - `src/pages/LandingPage.tsx` — full landing page component
  - `src/landing.css` — all original CSS custom properties, animations, layout
- `artifacts/api-server/src/routes/process.ts` — image processing API endpoints
  - `POST /api/process` — upload + process image (returns success JSON)
  - `GET /api/usage` — usage stats (placeholder)
  - `POST /api/signup` — generate API key (placeholder)

## Architecture decisions

- Migrated from Python/FastAPI + plain HTML to Node.js Express + React/Vite
- Image processing uses `sharp` (Node.js) instead of PIL/NumPy; applies noise, contrast, sharpness, saturation adjustments
- Landing page CSS is kept as a standalone `landing.css` file imported into the Vite CSS to preserve all original styles exactly
- API routes are in-memory placeholders; no database used yet (original also used SQLite for MVP)
- Signup/key generation is stateless demo mode — a real DB layer can be added later

## Product

AI Undetectable is a freemium API service that transforms AI-generated images to bypass AI detection tools (ZeroGPT, Copyleaks, etc.) by adding imperceptible noise, adjusting frequency characteristics, and re-encoding the image.

**Pricing:**
- Free: 10 images/month, 2MB max
- Pro: $9.99/month, 500 images, 10MB max
- Enterprise: Custom

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- `sharp` requires `onlyBuiltDependencies` entry in `pnpm-workspace.yaml` to run its install script
- Processed images are returned as JSON metadata (not binary) in the current implementation; a full download flow needs storage (S3/R2)
- The original backend was Python/FastAPI — the port to Express/Sharp replicates the same pipeline steps

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
- Original project files are in `.migration-backup/`

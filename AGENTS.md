# Repository Guidelines

## Project Structure & Module Organization
- `apps/backend/` holds the FastAPI service, Alembic migrations in `alembic/`, runtime code under `app/`, and scripts in `scripts/`.
- `apps/frontend/` is a Vite + React 18 SPA; `src/` contains UI modules, and `tests/` mirrors feature folders for component specs.
- Shared TypeScript utilities live in `packages/shared/`, while API type definitions are in `packages/types/`. Docker assets stay under `docker/` and the compose files at the root.

## Build, Test, and Development Commands
- Backend: `cd apps/backend && uvicorn app.main:app --reload` launches the API; use `pytest` for the unit suite and `alembic upgrade head` to migrate the database.
- Frontend: `cd apps/frontend && npm install` once, then `npm run dev` for the local dev server, `npm run build` for production bundles, and `npm run preview` to smoke-test builds.
- Full stack: use `docker-compose up -d` to spin the stack, and `docker-compose exec backend alembic upgrade head` after config changes.

## Coding Style & Naming Conventions
- Python code follows PEP 8 with auto-formatting via `black`; keep modules snake_case and classes in PascalCase.
- TypeScript uses 2-space indentation, `eslint` + `@typescript-eslint` rules, and kebab-case for file names (`recordings-table.tsx`).
- CSS lives in Tailwind utility classes; co-locate component styles with the component.

## Testing Guidelines
- Backend: write `pytest` cases beside code in `tests/` using `test_*.py` names; include async scenarios with `pytest-asyncio`. Run `pytest --cov=app` before PRs and keep coverage stable.
- Frontend: add Vitest specs under `apps/frontend/tests/` with `*.test.ts(x)` or `*.spec.ts(x)` files. Use Testing Library for DOM assertions and prefer testing observable behavior.

## Commit & Pull Request Guidelines
- Match the existing history format (`[YYMMDD] short summary`), keeping subjects in present tense and under ~72 characters.
- Squash small fixups before submitting. PRs should describe the change set, link tracking issues, note migrations or env changes, and include screenshots or terminal output when UI or CLI behavior shifts.
- Verify `npm run lint` and `pytest` locally before opening a PR; CI assumes green pipelines.

## Environment & Configuration Tips
- Copy `.env.example` to `.env` for local runs; secure secrets are required for auth and AI integrations.
- Volume mounts in `docker-compose.yml` expect Unix paths—update them when running on alternative hosts.

# Task Tracker

## Current Snapshot
- Backend now serves authenticated user flows, automatic recording & schedule APIs, and Celery workers that simulate FFmpeg execution and cron-based dispatch. Schedule entries maintain `next_run_at` timestamps and dispatch Celery tasks via beat.
- Database configuration supports PostgreSQL in production while tests run on SQLite via adaptive types. The backend test suite covers auth, health, recordings, schedules, Celery orchestration, and schedule dispatch behaviour.
- Frontend provides login/registration pages with token persistence (Zustand + localStorage) and protects the dashboard while surfacing live health, recording, and schedule metrics via TanStack Query.
- Dependencies on both stacks install cleanly on Python 3.13 / Node 18, and `pytest` + `npm test -- --run` pass locally.

## Immediate Actions (Start Now)
1. **Frontend session polish** – add logout confirmation, token refresh handling, and surface API errors per field.
2. **Recording pipeline hardening** – replace FFmpeg simulation with real command execution, stream storage, and failure retries.
3. **Schedule management UX** – expose schedule CRUD (create/edit/deactivate) and next-run indicators in the dashboard.

## Near-Term Backlog
- Implement file management APIs (list/download/delete) and surface them in the UI, including storage usage charts.
- Expand user administration (role management, deactivation) and audit logging endpoints.
- Add integration tests (API + frontend) to the CI workflow and surface coverage artifacts reliably.
- Populate `packages/` with shared TypeScript/JSON schemas once API contracts stabilize.

## Known Risks / Follow-ups
- Celery tasks still simulate FFmpeg; ensure production workers handle long-running processes, storage quotas, and cancellation.
- croniter emits deprecation warnings under Python 3.13—track upstream fixes or patch with timezone-aware helpers.
- Ensure migrations reflect new columns (`next_run_at`) before deploying; SQLite fallback masks drift.

# Codebase Summary

## Root
- `index.html` — SPA đơn file: UI 5 trang + 4 module + chatbot + full-stack layer (auth + fetch API + fallback demo).
- `100.js` — bộ 100 intents JSON cho chatbot (`window.PHARMA_INTENTS = {...}`).
- `ke-hoach-*.md` — PRD v1 + v2 (đầu vào).

## backend/
- `app/` — FastAPI (xem `system-architecture.md`).
- `tests/` — pytest (19 tests: auth/workflow/data/ai/helpdesk).
- `requirements.txt` — deps chạy; `requirements-dev.txt` — pytest + httpx.
- `.env.example` — mẫu biến môi trường.

## frontend (nằm trong index.html)
- Theme: Tailwind CDN + custom colors `brand`/`gold`.
- Full-stack layer: `apiFetch`, `AUTH`, `boot()` (tự phát hiện backend), override module theo mode.

## plans/, docs/
- `plans/` — kế hoạch triển khai theo phase.
- `docs/` — tài liệu dự án (file này).

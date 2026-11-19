# System Architecture — Pharma Automation Hub

## Tổng quan
```
Browser ── index.html (SPA, Tailwind CDN)
   │  chạy qua backend:  fetch /api/v1/*  (JWT Bearer)
   │  chạy file trực tiếp: fallback demo mock
   ▼
FastAPI (backend/app) ── routers (auth/workflows/data/ai/helpdesk)
   │
   ▼
SQLAlchemy ORM ── SQLite (default) / PostgreSQL (DATABASE_URL)
```

## Backend structure
```
backend/app/
├── main.py        # FastAPI app, CORS, static (index.html + 100.js), lifespan seed
├── config.py      # env: DATABASE_URL, SECRET_KEY, LLM_PROVIDER
├── database.py    # engine, SessionLocal, Base, get_db
├── models.py      # 11 bảng SQLAlchemy 2.0
├── schemas.py     # Pydantic v2 request/response
├── seed.py        # khởi tạo bảng + dữ liệu mẫu
├── deps.py        # get_current_user (JWT)
├── routers/       # auth, workflows, data, ai, helpdesk
└── services/      # auth_service (hash+JWT), data_service (pandas), ai_service (LLM+intents)
```

## Database schema (11 bảng)
- RBAC: `users`, `roles`, `departments`
- Workflow: `workflow_templates`, `workflow_tickets`, `workflow_logs`
- Data: `inventory_records`, `reconciliation_runs`, `discrepancy_details`
- AI: `ai_review_logs`
- Helpdesk: `it_tickets`, `it_assets`

## REST API (prefix `/api/v1`)
| Nhóm | Endpoint |
|---|---|
| Auth | POST `/auth/login`, GET `/auth/me` |
| Workflow | GET `/workflows/templates`, POST `/workflows/tickets`, GET `/workflows/tickets/kanban`, POST `/workflows/tickets/{id}/approve` |
| Data | POST `/data/upload-clean`, POST `/data/clean`, POST `/data/reconcile`, POST `/data/reconcile-json`, POST `/data/export-report` |
| AI | POST `/ai/process-task`, POST `/ai/review-submit`, POST `/ai/chatbot` |
| Helpdesk | POST/GET `/helpdesk/tickets`, GET `/assets` |

Tất cả endpoint nghiệp vụ yêu cầu `Authorization: Bearer <token>` (trừ login/health/root).

# Plan — Backend Full-stack Pharma Automation Hub (Tier 1)

## Mục tiêu
Xây backend FastAPI + SQLAlchemy (SQLite default, PostgreSQL-ready) theo v2, tái dùng frontend `index.html` hiện có (đổi localStorage → API).

## Quyết định kỹ thuật
- Python 3.12, FastAPI + Pydantic v2, SQLAlchemy 2.0.
- DB: SQLite default (`sqlite:///./pharma.db`), `DATABASE_URL` đổi sang Postgres.
- Auth: JWT (PyJWT) + hash mật khẩu pbkdf2 (stdlib).
- AI: `LLMProvider` mock default (100 intents + mô phỏng), pluggable provider thật.

## Cấu trúc
```
backend/
  requirements.txt
  .env.example
  app/
    main.py, config.py, database.py, models.py, schemas.py, seed.py
    routers/{auth,workflows,data,ai,helpdesk}.py
    services/{auth,workflow,data,ai,helpdesk}_service.py
  tests/
```

## DB Schema (v2 mục 2)
users, roles, departments; workflow_templates, workflow_tickets, workflow_logs;
inventory_records, reconciliation_runs, discrepancy_details;
ai_review_logs; it_tickets, it_assets.

## API (v2 mục 3)
- Auth: POST /auth/login, GET /auth/me
- Workflow: GET templates, POST tickets, GET tickets/kanban, POST tickets/{id}/approve
- Data: POST upload-clean, POST reconcile, GET export-report
- AI: POST process-task, POST review-submit, POST chatbot
- Helpdesk: POST/GET tickets, GET assets

## Phases
- [x] P0: Scaffolding (venv, requirements, config, database, models, schemas)
- [x] P1: Auth (login/me, JWT, seed users/roles/departments)
- [x] P2: Workflow engine API + seed templates (có quy tắc >10tr thêm bước Giám đốc)
- [x] P3: Data & reconciliation API (pandas/openpyxl, 4 trạng thái, xuất 4 sheet)
- [x] P4: AI API (process-task, review-submit, chatbot) + LLM provider mock
- [x] P5: Helpdesk & assets API (SLA countdown, serial/warranty)
- [x] P6: Frontend rewire (index.html → API) + login screen (workflow/helpdesk/AI/chatbot qua API; module Data vẫn xử lý client-side SheetJS)
- [ ] P7: Viết pytest tự động + docs

## Kết quả smoke test (đã chạy)
login/me, templates, create ticket (>10tr thêm bước Giám đốc), kanban, approve, chatbot, classify, helpdesk, assets, auth 401 — tất cả PASS. data_service (clean/reconcile/xlsx) unit-test PASS. Frontend login overlay + full-stack layer: syntax OK, phục vụ qua FastAPI OK.

## Success criteria
- `uvicorn backend.app.main:app` chạy, `GET /docs` hiện Swagger.
- Auth đăng nhập được; 4 module hoạt động qua API (không còn localStorage).
- Seed data đầy đủ (roles, users, 3 workflow templates, thuốc mẫu, 100 intents).

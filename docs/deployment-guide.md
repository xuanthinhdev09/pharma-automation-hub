# Deployment Guide

## Chạy local (Full-stack)
```bash
# 1. tạo venv + cài deps
python3 -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt

# 2. chạy backend
.venv/Scripts/python.exe -m uvicorn backend.app.main:app --reload
# mở http://127.0.0.1:8000  -> đăng nhập admin / demo123
# Swagger: http://127.0.0.1:8000/docs
```

## Chạy Static (không backend)
Mở trực tiếp `index.html` bằng trình duyệt → tự chạy demo mock (không cần đăng nhập).

## Deploy Static — GitHub Pages
1. Tạo repo GitHub, push `index.html` + `100.js`.
2. Settings → Pages → Source: Deploy from branch (hoặc dùng workflow `.github/workflows/`).
3. Link: `https://<user>.github.io/<repo>/`.
> Lưu ý: bản static không có backend → chỉ chạy module demo (mock), không có đăng nhập/DB.

## Deploy Full-stack — Render/Railway
1. Đẩy toàn bộ repo lên GitHub.
2. Render: New Web Service → Build: `pip install -r backend/requirements.txt`; Start: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
3. Đặt env `DATABASE_URL` (Postgres) — SQLite không bền trên host serverless.
4. Cấp `SECRET_KEY` mạnh trong env.

## Chạy tests
```bash
.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt
.venv/Scripts/python.exe -m pytest backend/tests
```

## Biến môi trường (`.env.example`)
`DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `LLM_PROVIDER`.

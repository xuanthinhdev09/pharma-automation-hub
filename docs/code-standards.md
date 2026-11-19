# Code Standards

## Python (backend)
- snake_case cho file/hàm/biến; PascalCase cho class.
- FastAPI: router mỏng (HTTP) → gọi `services/` cho logic nghiệp vụ.
- Schema request/response đặt trong `schemas.py` (Pydantic v2, `model_config from_attributes` cho Out).
- Mật khẩu: pbkdf2 (stdlib); token: JWT (PyJWT). Không commit secret.
- DB: SQLAlchemy 2.0 `Mapped`/`mapped_column`; FK nhiều chiều dùng string ref trong `relationship`.

## JS (frontend, index.html)
- kebab-case cho file; camelCase cho hàm.
- Một file `index.html` (theo PRD), chấp nhận >200 dòng (ngoại lệ so với quy tắc modularize).
- Full-stack layer: `apiFetch` + `AUTH` + `boot()`; mỗi module override theo mode (API/demo).

## Quy tắc chung
- YAGNI, KISS, DRY.
- Mock data tách rõ (demo), không lẫn dữ liệu thật.
- Lỗi trả JSON `{"detail": "..."}`; auth 401.

# Project Overview & PRD — Pharma Automation Hub

## Mục tiêu
Website demo minh họa năng lực **IT ứng dụng & tự động hóa ngành Dược/Thiết bị y tế**. Biến các yêu cầu công việc thành module phần mềm chạy được với dữ liệu giả lập.

## Kiến trúc 2 tầng (Dual-Tier)
| | Tầng 1: Full-stack | Tầng 2: Static SPA |
|---|---|---|
| Backend | FastAPI (async) | Không |
| DB | SQLAlchemy (SQLite default, PostgreSQL-ready) | localStorage |
| Frontend | index.html gọi API (fetch) | index.html thuần JS + CDN |
| Excel | pandas/openpyxl | SheetJS |
| AI | LLM provider mock + 100 intents | Simulated + 100 intents |

## 4 Module
1. **Workflow Designer** — luồng duyệt 4 bước, form đề xuất, Kanban, SLA. Mua hàng >10tr tự thêm bước Giám đốc.
2. **Data & Report Automation** — upload Excel/CSV, làm sạch, đối chiếu Kho vs Kế toán (4 trạng thái), Chart.js, xuất .xlsx 4 sheet.
3. **AI Assistant Workspace** — 4 tác vụ AI + khung Human-in-the-loop + chatbot 100 intents + 4 quy tắc an toàn.
4. **IT Helpdesk & KB** — ticket (SLA 1h/4h/1ngày/3ngày), knowledge base, tài sản IT.

## Disclaimer
Toàn bộ dữ liệu là giả lập. Footer: "Website demo — Dữ liệu giả lập". Không chứa thông tin thật của doanh nghiệp nào.

## Tài khoản demo
`admin / demo123` (IT_ADMIN). Thêm: `nhanvien`, `truongphong`, `ketoan`, `giamdoc` (cùng mật khẩu).

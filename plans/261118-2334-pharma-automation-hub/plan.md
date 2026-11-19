# Kế hoạch triển khai — Pharma Automation Hub (Static SPA)

## Tổng quan
Website demo năng lực tự động hóa ngành dược. Static SPA, Tailwind CDN, mock data 100%. Không backend, không thông tin ứng tuyển.

## Phạm vi (đã chốt với user)
- Nav: Trang chủ, Bản đồ JD, Module 1 (Workflow), Module 2 (Data Automation), Module 3 (AI Workspace), Module 4 (IT Helpdesk).
- Bỏ: trang Về tôi, thông tin ứng tuyển, hạn nộp hồ sơ, CV/GitHub.
- Chatbot dùng bộ 100 intents từ `100.js`.

## Tech
- Tailwind CDN, Chart.js 4.4.1, SheetJS 0.18.5, FontAwesome 6.5.1, Google Fonts Be Vietnam Pro.
- Theme: Burgundy `#800020` + Gold `#D4AF37`, nền `#F9FAFB`.
- localStorage lưu trạng thái (phiếu workflow, ticket).

## Files
- `index.html` — toàn bộ SPA (HTML + CSS + JS).
- `100.js` — bộ intents, wrap thành `window.PHARMA_INTENTS`.

## Phases
- [x] Phase 1: Khung SPA + nav + theme + trang chủ + Bản đồ JD
- [x] Phase 2: Module 2 — Data & Report Automation (upload/làm sạch/đối chiếu/Chart.js/xuất xlsx)
- [x] Phase 3: Module 1 — Workflow Designer (3 quy trình, luồng 4 bước, Kanban, SLA)
- [x] Phase 4: Module 3 — AI Workspace (4 demo case, khung đánh giá, chatbot 100 intents)
- [x] Phase 5: Module 4 — IT Helpdesk (ticket, KB, tài sản IT, biểu đồ) + responsive + footer
- [ ] Phase 6: Test trình duyệt (mở Chrome/Edge/Safari/mobile) — cần người dùng

## Success Criteria
- Mở `index.html` trực tiếp trên Chrome/Edge/Safari/mobile chạy đủ 6 trang + chatbot.
- CDN nạp ổn định; SheetJS xuất `.xlsx` thật; Chart.js vẽ đúng.
- Toàn bộ dữ liệu là mock, footer ghi "Website demo — Dữ liệu giả lập".

## Ghi chú
- PRD yêu cầu "1 file HTML duy nhất" → ngoại lệ so với quy tắc modularize 200 dòng (giữ nguyên theo spec).
- File `100.js` hiện thiếu dấu đóng `]}` ở cuối → sửa khi wrap.

# Design Guidelines

## Màu sắc
- Primary: Burgundy `#800020` (Tailwind `brand.600`; thang `brand.50–900`).
- Accent: Gold `#D4AF37` (Tailwind `gold.500`).
- Nền: `#F9FAFB`; thẻ trắng `border-slate-100`; trạng thái: emerald (ok), amber (warn), red (lỗi/quá hạn).

## Typography
- Font: **Be Vietnam Pro** (Google Fonts), fallback `system-ui`.

## Component
- Sidebar cố định (desktop) + drawer (mobile) — nav đổi màu brand khi active.
- Metric cards, data table, Kanban 3 cột, modal form, chat widget góc phải.
- Login overlay toàn màn hình khi chạy backend.

## Responsive
- Mobile: top bar + hamburger; grid tự gọn 1 cột; bảng có scroll ngang.
- Breakpoint chính: `lg` (sidebar), `md` (grid 2 cột).

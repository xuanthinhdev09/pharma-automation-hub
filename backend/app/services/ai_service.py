"""AI: LLM provider (mock mặc định) + chatbot 100 intents + 4 tác vụ nghiệp vụ."""
import json
import os
import random
import re
import unicodedata

INTENTS: dict | None = None


def _remove_diacritics(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


def _normalize(s: str) -> str:
    s = _remove_diacritics(s.lower())
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _load_intents() -> dict:
    global INTENTS
    if INTENTS is not None:
        return INTENTS
    candidates = [
        os.path.join(os.getcwd(), "100.js"),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "100.js"),
    ]
    text = None
    for path in candidates:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            break
    if text is None:
        INTENTS = {"intents": [], "fallback": ["Mình chưa hiểu câu hỏi này."], "suggested_questions": []}
        return INTENTS
    text = text.strip()
    if "=" in text:
        text = text.split("=", 1)[1].strip()
    if text.endswith(";"):
        text = text[:-1].strip()
    INTENTS = json.loads(text)
    return INTENTS


def match_intent(message: str) -> str:
    """So khớp keyword (bỏ dấu) với bộ intents; trả fallback khi điểm = 0."""
    intents = _load_intents()
    nq = _normalize(message)
    best = None
    best_score = 0
    best_len = 0
    for it in intents.get("intents", []):
        score = 0
        max_len = 0
        for kw in it.get("keywords", []):
            nk = _normalize(kw)
            if nk and nk in nq:
                score += 1
                max_len = max(max_len, len(nk))
        if score > best_score or (score == best_score and score > 0 and max_len > best_len):
            best, best_score, best_len = it, score, max_len
    if best is not None:
        return best["answer"]
    fallback = intents.get("fallback") or ["Mình chưa hiểu câu hỏi này."]
    return random.choice(fallback)


def process_task(task_type: str, input_text: str) -> tuple[str, int]:
    """Mô phỏng 4 tác vụ AI (mock provider). Trả về (output, confidence_score)."""
    t = input_text.strip()
    if task_type == "summarize":
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]
        out = "• Tóm tắt:\n" + (" ".join(sents[:3]) or t) + "\n\n• Số liệu chính: cần đối chiếu nguồn.\n• Việc cần làm: kiểm tra lại số liệu trước khi dùng."
    elif task_type == "email":
        out = f"Chủ đề: V/v {t[:60]}\n\nKính gửi [Tên người nhận],\n\n{t}.\n\nTrân trọng,\n[Người gửi]"
    elif task_type == "classify":
        n = _normalize(t)
        grp = ("Phần cứng" if re.search(r"(may in|printer|may tinh|laptop|man hinh)", n)
               else "Tài khoản" if re.search(r"(mat khau|dang nhap|tai khoan)", n)
               else "Mạng" if re.search(r"(wifi|mang|internet|vpn)", n)
               else "Phần mềm")
        prio = "Khẩn" if re.search(r"(khan|gap|mat mang|khong lam viec|khong in)", n) else "Trung bình"
        out = f"Nhóm đề xuất: {grp}\nMức ưu tiên: {prio}"
    elif task_type == "ocr":
        out = "Số hóa đơn: HD-2026-0118\nNgày: 18/11/2026\nNhà cung cấp: Công ty Dược Mẫu\nTổng tiền: 12.500.000 đ"
    else:
        out = "Không hỗ trợ tác vụ này."
    return out, 80

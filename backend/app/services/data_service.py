"""Xử lý dữ liệu: parse Excel/CSV (pandas), làm sạch, đối chiếu Kho vs Kế toán."""
import io
import re
import unicodedata

import pandas as pd

# Ánh xạ tên cột phổ biến (Anh/Việt) về khóa chuẩn
_COLUMN_ALIASES = {
    "item_code": ["item_code", "code", "mã hàng", "ma hang", "mã", "ma", "itemcode"],
    "item_name": ["item_name", "name", "tên", "ten", "tên thuốc", "ten thuoc", "tên sản phẩm", "ten san pham"],
    "generic_name": ["generic_name", "generic", "hoạt chất", "hoat chat", "tên gốc", "ten goc"],
    "batch_number": ["batch_number", "lot", "số lô", "so lo", "batch", "lô", "lo", "batch_no"],
    "expiry_date": ["expiry_date", "expiry", "hạn dùng", "han dung", "hạn", "han", "hết hạn", "het han"],
    "quantity_stock": ["quantity_stock", "quantity", "qty", "số lượng", "so luong", "stock", "tồn", "ton", "tồn kho", "ton kho"],
    "unit": ["unit", "đơn vị", "don vi", "đvt", "dvt"],
    "storage_condition": ["storage_condition", "bảo quản", "bao quan", "điều kiện", "dieu kien"],
}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    alias_map = {}
    for canon, aliases in _COLUMN_ALIASES.items():
        for a in aliases:
            alias_map[_norm(a)] = canon
    rename = {}
    for col in df.columns:
        n = _norm(col)
        if n in alias_map and col not in rename.values():
            rename[col] = alias_map[n]
    return df.rename(columns=rename)


def parse_upload(filename: str, content: bytes) -> list[dict]:
    buf = io.BytesIO(content)
    if filename.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(buf)
    else:
        df = pd.read_csv(buf)
    df = _normalize_columns(df)
    df = df.where(pd.notnull(df), "")
    rows = df.to_dict(orient="records")
    return [dict(r) for r in rows]


def clean_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    before = len(rows)
    seen = set()
    cleaned = []
    for r in rows:
        key = (str(r.get("item_code", "")).strip(), str(r.get("batch_number", "")).strip())
        if key[0] or key[1]:
            if key in seen:
                continue
            seen.add(key)
        cleaned.append(r)
    dup = before - len(cleaned)

    name_fixed = 0
    for r in cleaned:
        name = str(r.get("item_name", "")).strip()
        if name:
            fixed = re.sub(r"\s+", " ", name).title()
            if fixed != name:
                r["item_name"] = fixed
                name_fixed += 1

    empty = 0
    for r in cleaned:
        if any(str(r.get(k, "")).strip() == "" for k in ("item_code", "item_name", "batch_number", "expiry_date")):
            empty += 1

    log = [
        f"Bỏ {dup} dòng trùng lặp (theo Mã hàng + Số lô).",
        f"Chuẩn hóa {name_fixed} tên thuốc.",
        f"Đánh dấu {empty} dòng thiếu dữ liệu quan trọng.",
    ]
    return cleaned, log


def reconcile(warehouse: list[dict], accounting: list[dict]) -> tuple[list[dict], dict]:
    def key(r):
        return (str(r.get("item_code", "")).strip(), str(r.get("batch_number", "")).strip())

    def qty(r):
        v = r.get("quantity_stock", r.get("qty", 0))
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    table: dict = {}
    for r in warehouse:
        table[key(r)] = {"item_code": str(r.get("item_code", "")).strip(), "batch_number": str(r.get("batch_number", "")).strip(),
                         "qty_warehouse": qty(r), "qty_accounting": 0.0, "has_w": True, "has_a": False}
    for r in accounting:
        k = key(r)
        if k in table:
            table[k]["qty_accounting"] = qty(r)
            table[k]["has_a"] = True
        else:
            table[k] = {"item_code": str(r.get("item_code", "")).strip(), "batch_number": str(r.get("batch_number", "")).strip(),
                        "qty_warehouse": 0.0, "qty_accounting": qty(r), "has_w": False, "has_a": True}

    rows = []
    matched = disc = 0
    for v in table.values():
        diff = v["qty_warehouse"] - v["qty_accounting"]
        if v["has_w"] and v["has_a"]:
            status = "Khớp 100%" if diff == 0 else "Lệch số lượng"
            if diff == 0:
                matched += 1
            else:
                disc += 1
        elif v["has_w"]:
            status = "Chỉ có ở Kho"
            disc += 1
        else:
            status = "Chỉ có ở Kế toán"
            disc += 1
        rows.append({"item_code": v["item_code"], "batch_number": v["batch_number"],
                     "qty_warehouse": v["qty_warehouse"], "qty_accounting": v["qty_accounting"],
                     "difference": diff, "status": status})

    return rows, {"total": len(rows), "matched": matched, "discrepancy": disc}


def build_report_xlsx(clean: list[dict], discrepancy: list[dict], audit_log: list[str]) -> io.BytesIO:
    """Xuất Excel 4 sheet: Summary, Clean, Discrepancy, Audit Log."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary = pd.DataFrame([{"total_rows": len(clean), "total_discrepancy": len(discrepancy)}])
        summary.to_excel(writer, sheet_name="Summary", index=False)
        pd.DataFrame(clean).to_excel(writer, sheet_name="Clean", index=False)
        pd.DataFrame(discrepancy).to_excel(writer, sheet_name="Discrepancy", index=False)
        pd.DataFrame({"step": list(range(1, len(audit_log) + 1)), "log": audit_log}).to_excel(
            writer, sheet_name="Audit Log", index=False)
    output.seek(0)
    return output

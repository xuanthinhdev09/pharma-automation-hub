from backend.app.services import data_service


def test_clean_rows_dedup_and_normalize():
    rows = [
        {"item_code": "MED001", "item_name": "paracetamol", "batch_number": "LOT1", "expiry_date": "2026-12-31", "quantity_stock": 100},
        {"item_code": "MED001", "item_name": "paracetamol", "batch_number": "LOT1", "expiry_date": "2026-12-31", "quantity_stock": 100},
        {"item_code": "MED002", "item_name": "  vitamin c ", "batch_number": "LOT2", "expiry_date": "2026-12-31", "quantity_stock": 90},
    ]
    cleaned, _ = data_service.clean_rows(rows)
    assert len(cleaned) == 2
    names = {r["item_name"] for r in cleaned}
    assert "Vitamin C" in names


def test_reconcile_states():
    wh = [
        {"item_code": "MED001", "batch_number": "LOT1", "quantity_stock": 1000},
        {"item_code": "MED005", "batch_number": "LOT5", "quantity_stock": 780},
    ]
    ac = [
        {"item_code": "MED001", "batch_number": "LOT1", "quantity_stock": 950},
        {"item_code": "MED006", "batch_number": "LOT6", "quantity_stock": 200},
    ]
    rows, summary = data_service.reconcile(wh, ac)
    statuses = {r["status"] for r in rows}
    assert statuses == {"Lệch số lượng", "Chỉ có ở Kho", "Chỉ có ở Kế toán"}
    assert summary["discrepancy"] == 3


def test_clean_endpoint(auth, client):
    r = client.post("/api/v1/data/clean", headers=auth,
                    json={"rows": [{"item_code": "A", "item_name": " x ", "batch_number": "B"}]})
    assert r.status_code == 200
    assert r.json()["rows"][0]["item_name"] == "X"


def test_reconcile_json_endpoint(auth, client):
    r = client.post("/api/v1/data/reconcile-json", headers=auth,
                    json={"warehouse": [{"item_code": "MED001", "batch_number": "LOT1", "quantity_stock": 1000}],
                          "accounting": [{"item_code": "MED001", "batch_number": "LOT1", "quantity_stock": 950}]})
    assert r.status_code == 200
    assert r.json()["rows"][0]["status"] == "Lệch số lượng"

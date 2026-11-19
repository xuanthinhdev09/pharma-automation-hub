def test_templates(auth, client):
    r = client.get("/api/v1/workflows/templates", headers=auth)
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_create_ticket_above_limit_adds_director(auth, client):
    r = client.post("/api/v1/workflows/tickets", headers=auth,
                    json={"template_id": 1, "data_json": {"item": "Máy đo HA", "amount": "12000000"}})
    assert r.status_code == 200
    steps = r.json()["data_json"]["_steps"]
    assert any("Giám đốc" in s for s in steps)


def test_create_ticket_below_limit_no_director(auth, client):
    r = client.post("/api/v1/workflows/tickets", headers=auth,
                    json={"template_id": 1, "data_json": {"item": "Giấy in", "amount": "500000"}})
    assert r.status_code == 200
    steps = r.json()["data_json"]["_steps"]
    assert not any("Giám đốc" in s for s in steps)


def test_approve_to_completion(auth, client):
    r = client.post("/api/v1/workflows/tickets", headers=auth,
                    json={"template_id": 3, "data_json": {"content": "Chi phí vận chuyển"}})
    tid = r.json()["id"]
    # payment: 4 bước -> cần 3 lần approve để hoàn tất
    for _ in range(3):
        r = client.post(f"/api/v1/workflows/tickets/{tid}/approve", headers=auth, json={"action": "approve"})
    assert r.json()["status"] == "approved"


def test_reject_ticket(auth, client):
    r = client.post("/api/v1/workflows/tickets", headers=auth,
                    json={"template_id": 2, "data_json": {"type": "Nghỉ phép năm"}})
    tid = r.json()["id"]
    r = client.post(f"/api/v1/workflows/tickets/{tid}/approve", headers=auth, json={"action": "reject"})
    assert r.json()["status"] == "rejected"

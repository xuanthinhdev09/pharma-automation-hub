def test_create_ticket_has_sla(auth, client):
    r = client.post("/api/v1/helpdesk/tickets", headers=auth,
                    json={"category": "Máy in", "priority": "Khẩn", "subject": "Kẹt giấy", "description": "..."})
    assert r.status_code == 200
    assert r.json()["sla_due_date"] is not None
    assert r.json()["status"] == "Mới"


def test_list_tickets(auth, client):
    r = client.get("/api/v1/helpdesk/tickets", headers=auth)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_assets_seeded(auth, client):
    r = client.get("/api/v1/assets", headers=auth)
    assert r.status_code == 200
    assert len(r.json()) >= 4

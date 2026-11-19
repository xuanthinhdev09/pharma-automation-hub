def test_login_ok(client):
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "demo123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "sai"})
    assert r.status_code == 401


def test_me(auth, client):
    r = client.get("/api/v1/auth/me", headers=auth)
    assert r.status_code == 200
    assert r.json()["role_name"] == "IT_ADMIN"


def test_me_no_auth(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401

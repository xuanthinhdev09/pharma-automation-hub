"""Fixtures dùng chung — DB test riêng biệt, không đụng pharma.db."""
import os
import tempfile

# Phải set DATABASE_URL TRƯỚC khi import app (engine tạo lúc import)
_TEST_DB = os.path.join(tempfile.gettempdir(), "pharma_test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="session")
def client():
    if os.path.exists(_TEST_DB):
        os.remove(_TEST_DB)
    # lifespan (startup) gọi seed.init_db() -> tạo bảng + dữ liệu mẫu
    with TestClient(app) as c:
        yield c
    # Không xóa file ở teardown: SQLite engine còn giữ handle trên Windows.
    # File sẽ được xóa ở đầu lần chạy sau (setup).


@pytest.fixture(scope="session")
def auth(client):
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "demo123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

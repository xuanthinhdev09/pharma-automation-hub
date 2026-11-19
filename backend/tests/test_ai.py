from backend.app.services import ai_service


def test_match_intent():
    ans = ai_service.match_intent("Quy trình duyệt gồm những bước nào?")
    assert "bước" in ans


def test_process_task_classify_no_diacritics():
    out, _ = ai_service.process_task("classify", "máy in tầng 2 kẹt giấy")
    assert "Phần cứng" in out


def test_chatbot_endpoint(auth, client):
    r = client.post("/api/v1/ai/chatbot", headers=auth, json={"message": "quên mật khẩu thì sao"})
    assert r.status_code == 200
    assert len(r.json()["answer"]) > 0

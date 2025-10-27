def test_login_demo_ok(client):
    res = client.post("/api/v1/auth/login", json={"email":"admin@vitalband.local","password":"Admin123!"})
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data

def test_login_demo_bad(client):
    res = client.post("/api/v1/auth/login", json={"email":"", "password":""})
    assert res.status_code == 401

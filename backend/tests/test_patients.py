def test_list_patients(client):
    res = client.get("/api/v1/patients")
    assert res.status_code == 200
    data = res.get_json()
    assert "items" in data
    # estructura básica si hay elementos
    if data["items"]:
        p = data["items"][0]
        assert "id" in p and "full_name" in p
        assert "email" in p  # puede ser None

def test_admin_create_patient_requires_auth(client):
    # debe pedir JWT
    res = client.post("/api/v1/admin/patients", json={"first_name":"Test","last_name":"User"})
    assert res.status_code == 401

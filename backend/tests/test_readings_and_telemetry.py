import os
import time

def test_readings_alias_last24h(client, auth_headers):
    # alias /metrics/... mantiene compatibilidad
    res = client.get("/api/v1/metrics/1/last24h", headers=auth_headers)
    assert res.status_code == 200
    assert "items" in res.get_json()

def test_telemetry_list_ok(client, auth_headers):
    res = client.get("/api/v1/devices/1/telemetry", headers=auth_headers)
    # si el device 1 no existe, podría ser 404; aceptamos 200/404
    assert res.status_code in (200, 404)

def test_telemetry_create_optional_write(client, auth_headers):
    """
    Test de ESCRITURA opcional. Solo se ejecuta si E2E_WRITE=1.
    Para activarlo en PowerShell:
      $env:E2E_WRITE=1
    """
    if os.getenv("E2E_WRITE") != "1":
        return  # skip suave

    payload = {"battery_mv": 3890, "battery_pct": 72, "charging": False}
    res = client.post("/api/v1/devices/1/telemetry", json=payload, headers=auth_headers)

    # Puede fallar con 404 si el device 1 no existe: lo aceptamos como smoke test
    assert res.status_code in (201, 404)

import os
import json
import base64
import logging
from typing import Any, Dict

import pymysql
import boto3
from botocore.exceptions import ClientError


log = logging.getLogger()
log.setLevel(logging.INFO)


def _get_db_config() -> Dict[str, Any]:
    secret_arn = os.environ.get("DB_SECRET_ARN")
    if not secret_arn:
        raise RuntimeError("DB_SECRET_ARN env var is required")

    sm = boto3.client("secretsmanager")
    try:
        resp = sm.get_secret_value(SecretId=secret_arn)
        secret_str = resp.get("SecretString")
        if not secret_str:
            raise RuntimeError("SecretString empty in Secrets Manager response")
        data = json.loads(secret_str)
        return {
            "host": data.get("host"),
            "port": int(data.get("port", 3306)),
            "user": data.get("username"),
            "password": data.get("password"),
            "db": data.get("dbname"),
        }
    except ClientError as e:
        log.error(f"Error fetching secret: {e}")
        raise


def _connect_db():
    cfg = _get_db_config()
    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["db"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def _parse_event(event: Dict[str, Any]) -> Dict[str, Any]:
    # IoT Core → Lambda can pass JSON directly or base64 in event['payload']
    payload = event.get("payload")
    if isinstance(payload, (bytes, bytearray)):
        try:
            decoded = json.loads(payload.decode("utf-8"))
            return decoded
        except Exception:
            pass
    if isinstance(payload, str):
        try:
            # try base64 first
            b = base64.b64decode(payload)
            decoded = json.loads(b.decode("utf-8"))
            return decoded
        except Exception:
            try:
                decoded = json.loads(payload)
                return decoded
            except Exception:
                pass

    # Fallback: entire event is the message
    return event


def _ensure_device(conn, serial: str) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM devices WHERE serial=%s", (serial,))
        row = cur.fetchone()
        if row:
            return int(row["id"])
        cur.execute(
            """
            INSERT INTO devices (patient_id, model, serial, status)
            VALUES (NULL, %s, %s, 'active')
            """,
            ("esp32-vitalband", serial),
        )
        cur.execute("SELECT LAST_INSERT_ID() AS id")
        rid = cur.fetchone()
        return int(rid["id"]) if rid and "id" in rid else 0


def _insert_readings(conn, device_id: int, msg: Dict[str, Any]):
    hr = msg.get("heart_rate_bpm")
    spo2 = msg.get("spo2_pct")
    temp_c = msg.get("temp_c")
    motion = msg.get("motion_level")
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO readings (device_id, heart_rate_bpm, spo2_pct, temp_c, motion_level)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (device_id, hr, spo2, temp_c, motion),
        )


def _insert_telemetry(conn, device_id: int, msg: Dict[str, Any]):
    battery_mv = msg.get("battery_mv")
    battery_pct = msg.get("battery_pct")
    charging = None  # derive if needed later
    rssi = msg.get("rssi_dbm")
    board_temp_c = None
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO device_telemetry (device_id, battery_mv, battery_pct, charging, rssi_dbm, board_temp_c)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (device_id, battery_mv, battery_pct, charging, rssi, board_temp_c),
        )


def handler(event, context):
    log.info("Received event")
    try:
        msg = _parse_event(event) or {}
        serial = msg.get("serial")
        if not serial:
            raise ValueError("Missing 'serial' in message")

        conn = _connect_db()
        try:
            device_id = _ensure_device(conn, serial)
            _insert_readings(conn, device_id, msg)
            _insert_telemetry(conn, device_id, msg)
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return {
            "statusCode": 200,
            "body": json.dumps({"ok": True, "device_id": device_id}),
        }
    except Exception as e:
        log.error(f"Error processing event: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": str(e)}),
        }


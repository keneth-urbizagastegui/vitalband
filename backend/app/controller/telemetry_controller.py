from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..services.telemetry_service import TelemetryService
from ..model.dto.request_schemas import DeviceTelemetryRequest
from ..model.dto.response_schemas import DeviceTelemetryResponse

telemetry_bp = Blueprint("telemetry", __name__) 
_service = TelemetryService()
_in = DeviceTelemetryRequest()
_out = DeviceTelemetryResponse()
_out_many = DeviceTelemetryResponse(many=True)

def _parse_dt(s: str | None):
    if not s:
        return None
    # Acepta 'Z' y sin zona
    return datetime.fromisoformat(s.replace("Z", ""))

@telemetry_bp.post("/devices/<int:device_id>/telemetry")
@jwt_required()
def create_telemetry(device_id: int):
    payload = _in.load(request.get_json(force=True) or {})
    tel = _service.create(device_id, payload)
    return _out.dump(tel), 201

@telemetry_bp.get("/devices/<int:device_id>/telemetry")
@jwt_required()
def list_telemetry(device_id: int):
    dt_from = _parse_dt(request.args.get("from"))
    dt_to = _parse_dt(request.args.get("to"))
    limit = int(request.args.get("limit", 500))
    items = _service.list_by_device(device_id, dt_from, dt_to, limit)
    return {"items": _out_many.dump(items)}, 200

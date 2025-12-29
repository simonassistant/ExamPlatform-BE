import hashlib
import logging
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Iterable

def md5_encode(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()

def to_bool(text: str, default: bool = False)-> bool:
    if text is None or text=='':
        return default
    text = text.strip().lower()
    if default:
        return not (text == 'false' or text == '0')
    else:
        return text == 'true' or text == '1'

def to_datetime(text: str)-> datetime:
    format_str:str = '%Y-%m-%d %H:%M:%S' if text.find('-') >= 0 else '%Y/%m/%d %H:%M:%S'
    return datetime.strptime(text, format_str)

def respond_suc(data: dict) -> dict:
    return {
        "code": 0,
        "msg": "success",
        "data": data
    }

def respond_fail(code: int = -1, msg: str='fail', data: dict = None) -> dict:
    return {
        "code": code,
        "msg": msg,
        "data": data
    }


_AUDIT_REDACT_KEYS = {"password", "token", "secret", "answer", "correct_answer"}
_logger = logging.getLogger("examplatform.audit")


def redact_payload(payload: Dict[str, Any] | None) -> Dict[str, Any]:
    """Redact sensitive fields before logging audit events."""
    if payload is None:
        return {}
    clone = deepcopy(payload)
    for key in list(clone.keys()):
        if key.lower() in _AUDIT_REDACT_KEYS:
            clone[key] = "<redacted>"
        elif isinstance(clone[key], dict):
            clone[key] = redact_payload(clone[key])
    return clone


def emit_audit(event: str, payload: Dict[str, Any] | None = None, user_id: str | None = None):
    """Emit a structured audit log entry with basic redaction applied."""
    safe_payload = redact_payload(payload)
    _logger.info({
        "event": event,
        "user_id": user_id,
        "payload": safe_payload,
        "timestamp": datetime.utcnow().isoformat(),
    })

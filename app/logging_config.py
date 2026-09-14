# Phase 6d step 1: structured JSON logs on stdout (no extra packages).
#
# Containers should log to stdout/stderr; agents (later: Loki) collect from there.
# Shape is stable JSON so you can grep/jq — not free-form text.
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

# Extra keys we may attach via logger.info("...", extra={...}) in later steps.
_EXTRA_KEYS = (
    "request_id",
    "order_id",
    "handler",
    "method",
    "status",
    "event",
)


class JsonFormatter(logging.Formatter):
    """Turn a LogRecord into one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in _EXTRA_KEYS:
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the service logger once; safe to call on import."""
    logger = logging.getLogger("service-orders")
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger

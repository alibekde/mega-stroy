from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
import re
from typing import Any, Optional


def now_iso(tz: str) -> str:
    dt = datetime.now(timezone.utc).astimezone(ZoneInfo(tz))
    return dt.replace(microsecond=0).isoformat()


def parse_amount(text: str) -> Optional[int]:
    s = re.sub(r"[^\d]", "", text or "")
    if not s:
        return None
    try:
        val = int(s)
        return val if val >= 0 else None
    except ValueError:
        return None


def fmt_amount(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " so'm"


def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


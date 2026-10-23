"""ORM 公共部分：UTC 时间戳工具函数。"""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

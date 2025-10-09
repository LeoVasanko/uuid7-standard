from __future__ import annotations
from datetime import datetime
from datetime import timezone as _tz
from secrets import token_bytes as _token_bytes
from uuid import UUID

__all__ = ["create", "time"]

# Maximum value for 48-bit timestamp (approximately year 10889)
_MAX_TIMESTAMP_MS = (1 << 48) - 1


def create(when: datetime | None = None) -> UUID:
    """Create a UUIDv7 with timestamp-based ordering.

    Args:
        when: Timestamp to use. Defaults to current UTC time.
    """
    if when is None:
        when = datetime.now(_tz.utc)

    # Convert to millisecond timestamp
    ts_ms = int(when.timestamp() * 1000)

    # Validate timestamp range
    if ts_ms < 0:
        raise ValueError(
            f"Timestamp must be >= Unix epoch (1970-01-01 00:00:00 UTC), got {when}"
        )
    if ts_ms > _MAX_TIMESTAMP_MS:
        raise ValueError(
            f"Timestamp exceeds 48-bit limit (max ~year 10889), got {when}"
        )

    ts = ts_ms.to_bytes(6, "big")
    rand = bytearray(_token_bytes(10))
    rand[0] = (rand[0] & 0x0F) | 0x70
    rand[2] = (rand[2] & 0x3F) | 0x80
    return UUID(bytes=ts + rand)


def time(u: UUID | str) -> datetime:
    """Extract the timestamp from a UUIDv7.

    Raises ValueError if u is not a UUID version 7.
    """
    if not isinstance(u, UUID):
        u = UUID(u)
    if u.version != 7 or u.variant != "specified in RFC 4122":
        raise ValueError("Not a UUIDv7")
    ts = int.from_bytes(u.bytes[:6], "big")
    return datetime.fromtimestamp(ts / 1000, tz=_tz.utc)

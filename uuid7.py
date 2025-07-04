from datetime import datetime
from datetime import timezone as _tz
from secrets import token_bytes as _token_bytes
from uuid import UUID

__all__ = ["create", "time"]


def create(when: datetime | None = None) -> UUID:
    """Create a UUIDv7 with timestamp-based ordering.

    Args:
        when: Timestamp to use. Defaults to current time.
    """
    if when is None:
        when = datetime.now()
    ts = int(when.timestamp() * 1000).to_bytes(6, "big")
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
    if u.version != 7:
        raise ValueError("Not a UUIDv7")
    ts = int.from_bytes(u.bytes[:6], "big")
    return datetime.fromtimestamp(ts / 1000, tz=_tz.utc)

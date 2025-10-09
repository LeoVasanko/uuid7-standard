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

    UUIDv7 encodes a 48-bit timestamp (milliseconds since Unix epoch)
    followed by 74 random bits, providing both time-based ordering and
    sufficient randomness for distributed systems.

    Follows RFC 9562 specification for UUID version 7.

    Args:
        when: Timestamp to use. Must be a datetime object (timezone-aware
              or naive). Defaults to current UTC time.
              Must be >= 1970-01-01 and < year 10889.

    Returns:
        A valid UUIDv7 instance with version=7 and RFC 4122 variant.

    Raises:
        ValueError: If timestamp is before Unix epoch or too far in future.
        TypeError: If when is not a datetime object or None.
    """
    # Type validation
    if when is not None and not isinstance(when, datetime):
        raise TypeError(f"when must be datetime or None, got {type(when).__name__}")

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

    Args:
        u: A UUIDv7 instance or string representation.

    Returns:
        The timestamp as a timezone-aware datetime (UTC).

    Raises:
        ValueError: If u is not a valid UUIDv7 (wrong version or variant).
    """
    if not isinstance(u, UUID):
        u = UUID(u)
    if u.version != 7 or u.variant != "specified in RFC 4122":
        raise ValueError(f"Not a UUIDv7 (version={u.version}, variant={u.variant})")
    ts = int.from_bytes(u.bytes[:6], "big")
    return datetime.fromtimestamp(ts / 1000, tz=_tz.utc)

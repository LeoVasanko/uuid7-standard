# UUIDv7 for Python

A simple module for generating UUIDv7 that contain creation
timestamps. Another function for extracting the time of an UUID.

Note: As of writing, Python has no UUIDv7 support. There's an abandoned package `uuid7` that uses a draft RFC with incorrect timestamps (some two centuries off). These modules conflict, uninstall the other one.

- **Standard compliant**: Follows the final UUIDv7 [specification](https://www.rfc-editor.org/rfc/rfc9562.html#name-uuid-version-7).
- **Pythonic**: Uses stdlib `datetime` and `UUID` facilities rather than milliseconds or bare strings.

## Installation

```sh
pip install uuid7-standard
```

Or for your project using [uv](https://docs.astral.sh/uv/):
```sh
uv add uuid7-standard
```

## Usage

```python
import uuid7

# Create a random UUIDv7 with current timestamp
u = uuid7.create()
print(str(u), u.bytes)

# Create with specific timestamp
from datetime import datetime, UTC

when = datetime(1970, 1, 1, tzinfo=UTC)
u = uuid7.create(when)

# Extract timestamp
from uuid import UUID

u = UUID('00000000-0000-7dac-b3e3-ecb571bb3e2f')
timestamp = uuid7.time(u)  # 1970-01-01 UTC
```

### `create(when: datetime?) -> UUID`

Create a UUIDv7 with timestamp-based ordering.

**Parameters:**
- `when`: Optional datetime object. Defaults to current UTC time if not provided.
  - Must be a `datetime` instance (timezone-aware or naive)
  - Must be >= Unix epoch (1970-01-01 00:00:00 UTC)
  - Must be < year 10889 (48-bit timestamp limit)

**Returns:** A `UUID` instance with version 7 and RFC 4122 variant.

**Raises:**
- `TypeError`: If `when` is not a datetime object or None
- `ValueError`: If timestamp is before Unix epoch or exceeds 48-bit limit

**Note:** This is useful for creating multiple UUIDs with precisely the same timestamp.

### `time(u: UUID|str) -> datetime`

Extract the timestamp from a UUIDv7.

**Parameters:**
- `u`: A UUIDv7 instance or string representation

**Returns:** A timezone-aware `datetime` object in UTC.

**Raises:**
- `ValueError`: If the UUID is not a valid UUIDv7 (wrong version or variant)

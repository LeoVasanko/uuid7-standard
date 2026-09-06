# UUIDv7 for Python

A simple module for generating UUIDv7s with creation times, and for extracting the time from a UUID.

ℹ️ At the time of writing, Python had no UUIDv7 support. It does now, but still doesn't allow providing or extracting timestamps, which we do. Beware that there is also an abandoned package named `uuid7` that uses a draft RFC and produces all wrong timestamps.

- **Standards-compliant**: Follows the final UUIDv7 [specification](https://www.rfc-editor.org/rfc/rfc9562.html#name-uuid-version-7).
- **Pythonic**: Uses stdlib `datetime` and `UUID` facilities rather than (milli)seconds, custom UUID types, or bare strings, as used by alternatives such as `uuid7-rs`.
- **Lightweight**: A tiny pure-Python module with no dependencies, fast enough to process about a million UUIDv7s per second per CPU core.

## Installation

```sh
pip install uuid7-standard
```

Or, add to your project using [uv](https://docs.astral.sh/uv/):

```sh
uv add uuid7-standard
```

## Usage

```python
import uuid7
from datetime import datetime, UTC
from uuid import UUID

# Create a random UUIDv7 with the current timestamp, same as uuid.uuid7()
u = uuid7.create()
print(str(u), u.bytes)

# Create one with a specific timestamp
when = datetime(1970, 1, 1, tzinfo=UTC)
u = uuid7.create(when)

# Extract the timestamp
u = UUID('00000000-0000-7dac-b3e3-ecb571bb3e2f')
timestamp = uuid7.time(u)  # 1970-01-01 UTC
```

### `uuid7.create(when: datetime?) -> UUID`

Create a UUIDv7 with timestamp-based ordering.

The current time is used unless `when` is passed as a `datetime` (local time or timezone-aware). This is useful for creating multiple UUIDv7s with precisely the same timestamp.

### `uuid7.time(u: UUID|str) -> datetime`

Extract the timestamp from a UUIDv7. Raises `ValueError` if the UUID is not a UUIDv7.

### `uuid7.UUID`: re-export of stdlib UUID

Useful when you want to indicate explicitly that a value is expected to be UUIDv7 while avoiding a separate `import uuid`.

Note that `uuid7.UUID is uuid.UUID` and does not enforce the UUIDv7 format. It does, however, help humans and coding agents avoid accidentally using `uuid4()` when working with such values.

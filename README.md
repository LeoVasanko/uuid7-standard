# UUIDv7 for Python

A simple module for generating UUIDv7 that contain creation timestamps. Another function for extracting the time of an UUID.

ℹ️ As of writing, Python had no UUIDv7 support. Now it does, but doesn't allow providing nor extracting timestamps, which both are supported by this module. Beware there's also an abandoned package `uuid7` that uses a draft RFC with incorrect timestamps (some two centuries off).

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

# Create a random UUIDv7 with current timestamp, same as uuid.uuid7()
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

### `uuid7.create(when: datetime?) -> UUID`

Create a UUIDv7 with timestamp-based ordering.

The current time is used, unless `when` is passed as datetime (local time or timezone-aware) This is useful e.g. for creating a bunch of UUIDv7 with precisely the same timestamp.

### `uuid7.time(u: UUID|str) -> datetime`

Extract the timestamp from a UUIDv7. Raises ValueError if the UUID is not a UUIDv7.

### `uuid7.UUID` re-export of stdlib UUID

In case you wish to explicitly indicate in your code that something is supposed to be v7, and avoid `import uuid`. Note that it **is** `uuid.UUID`, and does not actually enforce v7 format. This is useful with humans and coding agents, to avoid them accidentally using `uuid4()` when dealing with it.

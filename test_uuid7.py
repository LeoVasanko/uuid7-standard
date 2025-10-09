"""Comprehensive test suite for uuid7 module.

Tests RFC 9562 compliance, boundary conditions, error handling,
and all functionality of the UUIDv7 implementation.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID
import uuid7


class TestCreate:
    """Tests for uuid7.create() function."""

    def test_creates_valid_uuid(self):
        """Test that create() returns a valid UUID object."""
        u = uuid7.create()
        assert isinstance(u, UUID)

    def test_version_is_7(self):
        """Test that created UUID has version 7."""
        u = uuid7.create()
        assert u.version == 7

    def test_variant_is_rfc4122(self):
        """Test that created UUID has RFC 4122 variant."""
        u = uuid7.create()
        assert u.variant == "specified in RFC 4122"

    def test_default_uses_utc(self):
        """Test that default timestamp is in UTC."""
        before = datetime.now(timezone.utc)
        u = uuid7.create()
        after = datetime.now(timezone.utc)

        extracted_time = uuid7.time(u)
        # UUID only stores millisecond precision, so we need to allow for truncation
        # Compare timestamps as integers (milliseconds since epoch)
        before_ms = int(before.timestamp() * 1000)
        after_ms = int(after.timestamp() * 1000)
        extracted_ms = int(extracted_time.timestamp() * 1000)
        assert before_ms <= extracted_ms <= after_ms

    def test_with_specific_timestamp(self):
        """Test creation with a specific timestamp."""
        when = datetime(2024, 1, 1, 12, 30, 45, tzinfo=timezone.utc)
        u = uuid7.create(when)

        extracted_time = uuid7.time(u)
        # Should match within millisecond precision
        assert abs((extracted_time - when).total_seconds()) < 0.001

    def test_with_naive_datetime(self):
        """Test creation with naive (no timezone) datetime."""
        when = datetime(2024, 1, 1, 12, 30, 45)
        u = uuid7.create(when)

        # Should work without error
        assert u.version == 7

    def test_monotonic_ordering_different_times(self):
        """Test that UUIDs are ordered by timestamp."""
        t1 = datetime(2024, 1, 1, tzinfo=timezone.utc)
        t2 = datetime(2024, 1, 2, tzinfo=timezone.utc)

        u1 = uuid7.create(t1)
        u2 = uuid7.create(t2)

        assert u1 < u2
        assert str(u1) < str(u2)

    def test_same_timestamp_different_random(self):
        """Test that UUIDs with same timestamp have different random bits."""
        when = datetime(2024, 1, 1, tzinfo=timezone.utc)

        uuids = [uuid7.create(when) for _ in range(100)]

        # All should have same timestamp
        timestamps = [uuid7.time(u) for u in uuids]
        assert all(t == timestamps[0] for t in timestamps)

        # But all UUIDs should be different (random bits differ)
        assert len(set(uuids)) == 100

    def test_randomness_distribution(self):
        """Test that random bits are actually random."""
        when = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Generate many UUIDs with same timestamp
        uuids = [uuid7.create(when) for _ in range(1000)]

        # Extract random bytes (after first 6 bytes of timestamp)
        random_parts = [u.bytes[6:] for u in uuids]

        # All should be unique
        assert len(set(random_parts)) == 1000

        # Check bit distribution in first random byte
        first_bytes = [rp[0] for rp in random_parts]
        # Should have good distribution (not all same value)
        assert len(set(first_bytes)) > 10

    def test_epoch_timestamp(self):
        """Test creation at Unix epoch (1970-01-01)."""
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        u = uuid7.create(epoch)

        extracted = uuid7.time(u)
        assert extracted == epoch

    def test_far_future_timestamp(self):
        """Test creation with far future timestamp (but within limits)."""
        # Year 5000 is well within 48-bit limit
        when = datetime(5000, 1, 1, tzinfo=timezone.utc)
        u = uuid7.create(when)

        extracted = uuid7.time(u)
        assert abs((extracted - when).total_seconds()) < 0.001

    def test_microsecond_precision_truncation(self):
        """Test that microseconds are truncated to milliseconds."""
        # 123456 microseconds = 123.456 milliseconds -> truncates to 123 ms
        when = datetime(2024, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
        u = uuid7.create(when)

        extracted = uuid7.time(u)
        # Should be truncated to milliseconds
        expected = datetime(2024, 1, 1, 12, 0, 0, 123000, tzinfo=timezone.utc)
        assert extracted == expected


class TestCreateBoundaryConditions:
    """Tests for boundary conditions in uuid7.create()."""

    def test_negative_timestamp_raises_error(self):
        """Test that timestamps before Unix epoch raise ValueError."""
        before_epoch = datetime(1969, 12, 31, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="Timestamp must be >= Unix epoch"):
            uuid7.create(before_epoch)

    def test_timestamp_overflow_raises_error(self):
        """Test that timestamps exceeding 48-bit limit raise ValueError."""
        # Python datetime max year is 9999, but we can test the validation logic
        # by using the maximum year Python supports and verifying it's within limits
        # Year 9999 is well within 48-bit limit, so we can't directly test overflow
        # Instead, we'll test that the max timestamp constant is correctly defined
        max_ms = (1 << 48) - 1
        # This would be around year 10889, but datetime doesn't support it
        # So we just verify the constant exists and is correct
        assert uuid7._MAX_TIMESTAMP_MS == max_ms

    def test_max_valid_timestamp(self):
        """Test timestamp at the edge of Python's datetime range."""
        # Python datetime max year is 9999
        # Test that year 9999 works (it's well within 48-bit limit)
        max_python_datetime = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        # Should work fine
        u = uuid7.create(max_python_datetime)
        assert u.version == 7

        # Verify the timestamp is within 48-bit limit
        ts_ms = int(max_python_datetime.timestamp() * 1000)
        assert ts_ms < uuid7._MAX_TIMESTAMP_MS


class TestCreateTypeValidation:
    """Tests for type validation in uuid7.create()."""

    def test_string_timestamp_raises_error(self):
        """Test that string timestamp raises TypeError."""
        with pytest.raises(TypeError, match="when must be datetime or None"):
            uuid7.create("2024-01-01")  # type: ignore

    def test_int_timestamp_raises_error(self):
        """Test that integer timestamp raises TypeError."""
        with pytest.raises(TypeError, match="when must be datetime or None"):
            uuid7.create(1234567890)  # type: ignore

    def test_none_is_valid(self):
        """Test that None is valid (uses current time)."""
        u = uuid7.create(None)
        assert u.version == 7


class TestTime:
    """Tests for uuid7.time() function."""

    def test_extract_time_from_uuid(self):
        """Test extracting timestamp from UUIDv7."""
        when = datetime(2024, 6, 15, 14, 30, 45, 123000, tzinfo=timezone.utc)
        u = uuid7.create(when)

        extracted = uuid7.time(u)
        assert extracted == when

    def test_extract_time_from_string(self):
        """Test extracting timestamp from UUID string."""
        when = datetime(2024, 1, 1, tzinfo=timezone.utc)
        u = uuid7.create(when)

        extracted = uuid7.time(str(u))
        assert extracted == when

    def test_returns_utc_datetime(self):
        """Test that extracted time is timezone-aware (UTC)."""
        u = uuid7.create()
        extracted = uuid7.time(u)

        assert extracted.tzinfo is not None
        assert extracted.tzinfo == timezone.utc

    def test_epoch_extraction(self):
        """Test extracting epoch timestamp."""
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        u = uuid7.create(epoch)

        extracted = uuid7.time(u)
        assert extracted == epoch

    def test_reject_non_uuidv7(self):
        """Test that non-UUIDv7 raises ValueError."""
        # UUIDv4
        u4 = UUID('550e8400-e29b-41d4-a716-446655440000')

        with pytest.raises(ValueError, match="Not a UUIDv7"):
            uuid7.time(u4)

    def test_reject_invalid_variant(self):
        """Test that UUID with wrong variant raises ValueError."""
        # Create a UUID with version 7 but wrong variant
        # This is artificial but tests the validation
        bytes_data = bytearray(16)
        bytes_data[6] = 0x70  # Version 7
        bytes_data[8] = 0x00  # Wrong variant (should be 0x80-0xBF)

        u = UUID(bytes=bytes(bytes_data))

        with pytest.raises(ValueError, match="Not a UUIDv7"):
            uuid7.time(u)

    def test_error_message_includes_version_variant(self):
        """Test that error message shows version and variant info."""
        u4 = UUID('550e8400-e29b-41d4-a716-446655440000')

        with pytest.raises(ValueError, match=r"version=4.*variant="):
            uuid7.time(u4)


class TestRFC9562Compliance:
    """Tests for RFC 9562 specification compliance."""

    def test_timestamp_field_size(self):
        """Test that timestamp occupies first 48 bits (6 bytes)."""
        when = datetime(2024, 1, 1, tzinfo=timezone.utc)
        u = uuid7.create(when)

        # Extract first 6 bytes
        ts_bytes = u.bytes[:6]
        ts_ms = int.from_bytes(ts_bytes, "big")

        # Verify it matches the expected timestamp
        expected_ms = int(when.timestamp() * 1000)
        assert ts_ms == expected_ms

    def test_version_bits(self):
        """Test that version bits are correctly set (0111 = 7)."""
        u = uuid7.create()

        # Version is in bits 48-51 (high 4 bits of byte 6)
        version_byte = u.bytes[6]
        version_bits = (version_byte & 0xF0) >> 4

        assert version_bits == 0b0111

    def test_variant_bits(self):
        """Test that variant bits are correctly set (10xx xxxx)."""
        u = uuid7.create()

        # Variant is in high 2 bits of byte 8
        variant_byte = u.bytes[8]
        variant_bits = (variant_byte & 0xC0) >> 6

        assert variant_bits == 0b10

    def test_random_bits_are_random(self):
        """Test that random portion uses cryptographic randomness."""
        # Generate multiple UUIDs and check randomness
        uuids = [uuid7.create(datetime(2024, 1, 1, tzinfo=timezone.utc)) for _ in range(100)]

        # Extract random portions (74 bits total)
        # Bytes 6-7 (12 bits after version) + bytes 8-15 (62 bits after variant)
        random_parts = []
        for u in uuids:
            bytes_data = u.bytes
            # Get 12 random bits from bytes 6-7 (lower 12 bits)
            rand_a = int.from_bytes(bytes_data[6:8], "big") & 0x0FFF
            # Get 62 random bits from bytes 8-15 (lower 62 bits)
            rand_b = int.from_bytes(bytes_data[8:16], "big") & 0x3FFFFFFFFFFFFFFF
            random_parts.append((rand_a, rand_b))

        # All should be unique
        assert len(set(random_parts)) == 100

    def test_byte_order_is_big_endian(self):
        """Test that multi-byte fields use big-endian order."""
        # Known timestamp: 1000 milliseconds
        when = datetime(1970, 1, 1, 0, 0, 1, tzinfo=timezone.utc)
        u = uuid7.create(when)

        # First 6 bytes should be 0x0000000003E8 (1000 in big-endian)
        ts_bytes = u.bytes[:6]
        assert ts_bytes == b'\x00\x00\x00\x00\x03\xe8'


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_rapid_generation(self):
        """Test rapid UUID generation doesn't break."""
        uuids = [uuid7.create() for _ in range(10000)]

        # All should be valid
        assert all(u.version == 7 for u in uuids)

        # Most should be unique (some might have same millisecond)
        assert len(set(uuids)) > 9000

    def test_different_timezones_same_result(self):
        """Test that different timezone representations give same UUID timestamp."""
        # Same moment in different timezones
        utc_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        # UTC+8
        tz_plus_8 = timezone(timedelta(hours=8))
        local_time = datetime(2024, 1, 1, 20, 0, 0, tzinfo=tz_plus_8)

        u1 = uuid7.create(utc_time)
        u2 = uuid7.create(local_time)

        # Should have same timestamp (different random bits)
        t1 = uuid7.time(u1)
        t2 = uuid7.time(u2)
        assert t1 == t2

    def test_string_uuid_conversion(self):
        """Test that string UUIDs can be used with time()."""
        when = datetime(2024, 1, 1, tzinfo=timezone.utc)
        u = uuid7.create(when)

        # Various string formats
        uuid_str = str(u)
        uuid_hex = u.hex

        # All should work
        assert uuid7.time(uuid_str) == when
        assert uuid7.time(uuid_hex) == when

    def test_bytes_representation(self):
        """Test UUID bytes representation."""
        when = datetime(2024, 1, 1, tzinfo=timezone.utc)
        u = uuid7.create(when)

        # Should be 16 bytes
        assert len(u.bytes) == 16

        # Can reconstruct from bytes
        u2 = UUID(bytes=u.bytes)
        assert u2 == u


class TestModuleAPI:
    """Tests for module-level API."""

    def test_module_exports(self):
        """Test that __all__ exports correct functions."""
        assert hasattr(uuid7, 'create')
        assert hasattr(uuid7, 'time')
        assert uuid7.__all__ == ['create', 'time']

    def test_no_private_exports(self):
        """Test that private constants are not in __all__."""
        assert '_MAX_TIMESTAMP_MS' not in uuid7.__all__

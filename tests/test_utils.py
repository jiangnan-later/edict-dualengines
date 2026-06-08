"""Tests for shared utility functions."""
from __future__ import annotations

import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))


def test_now_iso_uses_local_timezone_not_utc(monkeypatch):
    import utils

    class FixedDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            # Old implementation passes datetime.timezone.utc. The desired
            # behavior is to ask Python for the local timezone via astimezone().
            assert tz is None
            return cls(2026, 6, 6, 19, 30, 0)

        def astimezone(self, tz=None):
            assert tz is None
            return self.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))

    monkeypatch.setattr(utils.datetime, 'datetime', FixedDateTime)

    assert utils.now_iso() == '2026-06-06T19:30:00+08:00'

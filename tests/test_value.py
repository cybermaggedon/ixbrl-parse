"""Tests for value module."""

import pytest
import datetime
from ixbrl_parse.value import (
    Val, Boolean, Date, String, Float, MonthDay, Duration
)


class TestVal:
    """Test base Val class."""

    def test_string_value(self):
        """Test String value class."""
        val = String("test value")
        assert val.get_value() == "test value"
        assert str(val) == "test value"

    def test_string_no_unit(self):
        """Test that string values have no unit."""
        val = String("test")
        assert val.get_unit() is None


class TestBoolean:
    """Test Boolean value class."""

    def test_boolean_true(self):
        """Test boolean true value."""
        val = Boolean(True)
        assert val.get_value() is True
        assert str(val) == "True"

    def test_boolean_false(self):
        """Test boolean false value."""
        val = Boolean(False)
        assert val.get_value() is False
        assert str(val) == "False"


class TestDate:
    """Test Date value class."""

    def test_date_value(self):
        """Test date value."""
        val = Date("2020-12-31")
        assert val.get_value() == "2020-12-31"
        assert str(val) == "2020-12-31"


class TestFloat:
    """Test Float value class."""

    def test_float_without_unit(self):
        """Test float value without unit."""
        val = Float(3.14159)
        assert val.get_value() == 3.14159
        assert isinstance(val.get_value(), float)
        assert val.get_unit() == "None"

    def test_float_with_unit(self):
        """Test float value with unit."""
        val = Float(100.0, "GBP")
        assert val.get_value() == 100.0
        assert val.get_unit() == "GBP"
        assert "100" in str(val)
        assert "GBP" in str(val)


class TestMonthDay:
    """Test MonthDay value class."""

    def test_monthday_value(self):
        """Test month-day value."""
        val = MonthDay(12, 31)
        assert val.get_value() == "--12-31"
        assert str(val) == "--12-31"


class TestDuration:
    """Test Duration value class."""

    def test_duration_zero(self):
        """Test zero duration."""
        td = datetime.timedelta(days=0, seconds=0)
        val = Duration(td)
        assert val.get_value() == "P0D"

    def test_duration_days(self):
        """Test duration with days."""
        td = datetime.timedelta(days=5)
        val = Duration(td)
        assert "P" in val.get_value()
        assert "D" in val.get_value()

    def test_duration_complex(self):
        """Test complex duration."""
        td = datetime.timedelta(days=400, hours=2, minutes=30, seconds=15)
        val = Duration(td)
        result = val.get_value()
        assert result.startswith("P")
        # Should contain some time components
        assert len(result) > 2

from datetime import timedelta

from timescaledb.cleaners import clean_interval


def test_clean_interval_with_timedelta():
    # Test with 1 day timedelta
    interval = timedelta(days=1)
    value, type_ = clean_interval(interval)
    assert type_ == "INTEGER"
    assert value == 86400  # 1 day in seconds

    # Test with complex timedelta
    interval = timedelta(days=2, hours=3, minutes=15)
    value, type_ = clean_interval(interval)
    assert type_ == "INTEGER"
    assert value == 184500  # 2 days, 3 hours, 15 minutes in seconds


def test_clean_interval_with_integer():
    # Test with positive integer
    value, type_ = clean_interval(1000)
    assert type_ == "INTEGER"
    assert value == 1000

    # Test with zero
    value, type_ = clean_interval(0)
    assert type_ == "INTEGER"
    assert value == 0


def test_clean_interval_with_string():
    # Test with simple interval string
    value, type_ = clean_interval("1 day")
    assert type_ == "INTERVAL"
    assert value == "1 day"

    # Test with INTERVAL keyword
    value, type_ = clean_interval("INTERVAL 2 weeks")
    assert type_ == "INTERVAL"
    assert value == "2 weeks"

    # Test with quoted string
    value, type_ = clean_interval("INTERVAL '3 months'")
    assert type_ == "INTERVAL"
    assert value == "3 months"

    # Test with double quotes
    value, type_ = clean_interval('INTERVAL "4 days"')
    assert type_ == "INTERVAL"
    assert value == "4 days"


def test_clean_interval_with_invalid_type():
    # Test with float
    value, type_ = clean_interval(1.5)
    assert type_ == "INVALID"
    assert value == 1.5

    # Test with None
    value, type_ = clean_interval(None)
    assert type_ == "INVALID"
    assert value is None

    # Test with list
    value, type_ = clean_interval([])
    assert type_ == "INVALID"
    assert value == []

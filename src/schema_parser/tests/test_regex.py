import pytest

from schema_parser.core.exceptions import RegexFieldTypeError, RegexPatternMatchError
from schema_parser.functions.regex import RegexFunction


def test_regex_basic():
    """Test basic regex operation"""
    function = RegexFunction()
    data = {"log": "192.168.1.1 - GET /api [2024-01-01]"}
    result = function.execute(data=data, pattern="^(?P<ip>\\S+) .*", field="log")

    assert result["ip"] == "192.168.1.1"


def test_regex_with_nested_path():
    """Test regex with nested field path"""
    function = RegexFunction()
    data = {"event": {"log": "192.168.1.1 - GET /api [2024-01-01]"}}
    result = function.execute(data=data, pattern="^(?P<ip>\\S+) .*", field="event.log")

    assert result["ip"] == "192.168.1.1"


def test_regex_with_deeply_nested_path():
    """Test regex with deeply nested field path"""
    function = RegexFunction()
    data = {
        "level1": {
            "level2": {
                "log": "192.168.1.1 - GET /api [2024-01-01]",
            },
        },
    }
    result = function.execute(data=data, pattern="^(?P<ip>\\S+) .*", field="level1.level2.log")

    assert result["ip"] == "192.168.1.1"


def test_regex_missing_field():
    """Test that regex with missing field raises error"""
    function = RegexFunction()
    data = {"other": "value"}

    with pytest.raises(RegexPatternMatchError) as exc_info:
        function.execute(data=data, pattern="^test", field="missing")

    assert exc_info.value.field == "missing"


def test_regex_missing_nested_path():
    """Test that regex with missing nested path raises error"""
    function = RegexFunction()
    data = {"user": {"name": "John"}}

    with pytest.raises(RegexPatternMatchError) as exc_info:
        function.execute(data=data, pattern="^test", field="user.missing")

    assert exc_info.value.field == "user.missing"


def test_regex_invalid_field_type():
    """Test that regex with non-string field raises error"""
    function = RegexFunction()
    data = {"field": 123}

    with pytest.raises(RegexFieldTypeError) as exc_info:
        function.execute(data=data, pattern="^test", field="field")

    assert exc_info.value.field == "field"


def test_regex_pattern_no_match():
    """Test that regex with no match raises error"""
    function = RegexFunction()
    data = {"log": "no match here"}

    with pytest.raises(RegexPatternMatchError) as exc_info:
        function.execute(data=data, pattern="^test", field="log")

    assert exc_info.value.field == "log"


def test_regex_multiple_groups():
    """Test regex with multiple named groups"""
    function = RegexFunction()
    data = {"log": "192.168.1.1 - GET /api [2024-01-01 10:00:00]"}
    result = function.execute(
        data=data,
        pattern="^(?P<ip>\\S+) .* \\[(?P<time>[^\\]]+)\\]",
        field="log",
    )

    assert result["ip"] == "192.168.1.1"
    assert result["time"] == "2024-01-01 10:00:00"

import pytest

from schema_parser.core.exceptions import ParseJsonFunctionError
from schema_parser.functions.parse_json import ParseJsonFunction


def test_parse_json_simple_object():
    """Test parsing a simple JSON object"""
    function = ParseJsonFunction()
    data = {"json_field": '{"name": "John", "age": 30}'}
    result = function.execute(data=data, field="json_field")
    assert result == {"name": "John", "age": 30}


def test_parse_json_nested_object():
    """Test parsing a nested JSON object"""
    function = ParseJsonFunction()
    data = {"json_field": '{"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}}'}
    result = function.execute(data=data, field="json_field")
    assert result == {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}}


def test_parse_json_array_raises_error_when_not_in_place():
    """Test that parsing a JSON array raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": '[1, 2, 3, "four", true, null]'}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_array_of_objects_raises_error_when_not_in_place():
    """Test that parsing a JSON array of objects raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_string_raises_error_when_not_in_place():
    """Test that parsing a JSON string raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": '"Hello, World!"'}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_number_raises_error_when_not_in_place():
    """Test that parsing a JSON number raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": "42"}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_float_raises_error_when_not_in_place():
    """Test that parsing a JSON float raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": "3.14159"}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_boolean_true_raises_error_when_not_in_place():
    """Test that parsing a JSON boolean true raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": "true"}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_boolean_false_raises_error_when_not_in_place():
    """Test that parsing a JSON boolean false raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": "false"}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_null_raises_error_when_not_in_place():
    """Test that parsing a JSON null raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": "null"}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_empty_object():
    """Test parsing an empty JSON object"""
    function = ParseJsonFunction()
    data = {"json_field": "{}"}
    result = function.execute(data=data, field="json_field")
    assert result == {}


def test_parse_json_empty_array_raises_error_when_not_in_place():
    """Test that parsing an empty JSON array raises error when in_place=False"""
    function = ParseJsonFunction()
    data = {"json_field": "[]"}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert "unsupported data type" in str(exc_info.value).lower()


def test_parse_json_with_unicode():
    """Test parsing JSON with unicode characters"""
    function = ParseJsonFunction()
    data = {"json_field": '{"message": "Hello 世界", "emoji": "🎉"}'}
    result = function.execute(data=data, field="json_field")
    assert result == {"message": "Hello 世界", "emoji": "🎉"}


def test_parse_json_with_escaped_characters():
    """Test parsing JSON with escaped characters"""
    function = ParseJsonFunction()
    data = {"json_field": '{"path": "C:\\\\Users\\\\test", "quote": "He said \\"Hello\\""}'}
    result = function.execute(data=data, field="json_field")
    assert result == {"path": "C:\\Users\\test", "quote": 'He said "Hello"'}


def test_parse_json_invalid_json():
    """Test that invalid JSON raises ParseJsonFunctionError"""
    function = ParseJsonFunction()
    data = {"json_field": '{"name": "John", "age": }'}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert exc_info.value.field_value == '{"name": "John", "age": }'
    assert "Failed to load JSON from field `json_field`" in str(exc_info.value)


def test_parse_json_malformed_json():
    """Test that malformed JSON raises ParseJsonFunctionError"""
    function = ParseJsonFunction()
    data = {"json_field": "not valid json"}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert exc_info.value.field_value == "not valid json"
    assert "Failed to load JSON from field `json_field`" in str(exc_info.value)


def test_parse_json_missing_field():
    """Test that missing field silently ignores and returns data unchanged"""
    function = ParseJsonFunction()
    data = {"other_field": "value"}

    result = function.execute(data=data, field="json_field")

    # Should return data unchanged when field is not found
    assert result == data
    assert "other_field" in result


def test_parse_json_empty_string():
    """Test that empty string silently ignores and returns data unchanged"""
    function = ParseJsonFunction()
    data = {"json_field": "", "other_field": "value"}

    result = function.execute(data=data, field="json_field")

    # Should return data unchanged when field is empty string
    assert result == data
    assert "json_field" in result
    assert result["json_field"] == ""


def test_parse_json_field_is_none():
    """Test that field with None value silently ignores and returns data unchanged"""
    function = ParseJsonFunction()
    data = {"json_field": None, "other_field": "value"}

    result = function.execute(data=data, field="json_field", in_place=True)

    # Should return data unchanged when field is None
    assert result == data
    assert "json_field" in result
    assert result["json_field"] is None


def test_parse_json_field_is_none_not_in_place():
    """Test that field with None value silently ignores when not in_place"""
    function = ParseJsonFunction()
    data = {"json_field": None, "other_field": "value"}

    result = function.execute(data=data, field="json_field", in_place=False)

    # Should return data unchanged when field is None
    assert result == data
    assert "json_field" in result
    assert result["json_field"] is None


def test_parse_json_field_is_empty_list():
    """Test that field with empty list silently ignores and returns data unchanged"""
    function = ParseJsonFunction()
    data = {"json_field": [], "other_field": "value"}

    result = function.execute(data=data, field="json_field", in_place=True)

    # Empty list is treated as empty and should be ignored
    assert result == data
    assert "json_field" in result
    assert result["json_field"] == []


def test_parse_json_field_is_empty_dict():
    """Test that field with empty dict silently ignores and returns data unchanged"""
    function = ParseJsonFunction()
    data = {"json_field": {}, "other_field": "value"}

    result = function.execute(data=data, field="json_field", in_place=True)

    # Empty dict is treated as empty and should be ignored
    assert result == data
    assert "json_field" in result
    assert result["json_field"] == {}


def test_parse_json_field_is_zero():
    """Test that field with zero tries to parse it as JSON string and raises error"""
    function = ParseJsonFunction()
    data = {"json_field": 0, "other_field": "value"}

    # Zero is not empty, so it should try to parse it as JSON string
    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field", in_place=True)

    assert exc_info.value.field == "json_field"


def test_parse_json_field_is_false():
    """Test that field with False tries to parse it as JSON string and raises error"""
    function = ParseJsonFunction()
    data = {"json_field": False, "other_field": "value"}

    # False is not empty, so it should try to parse it as JSON string
    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field", in_place=True)

    assert exc_info.value.field == "json_field"


def test_parse_json_whitespace_only():
    """Test that whitespace-only string raises ParseJsonFunctionError"""
    function = ParseJsonFunction()
    data = {"json_field": "   "}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert exc_info.value.field_value == "   "
    assert "Failed to load JSON from field `json_field`" in str(exc_info.value)


def test_parse_json_incomplete_json():
    """Test that incomplete JSON raises ParseJsonFunctionError"""
    function = ParseJsonFunction()
    data = {"json_field": '{"name": "John"'}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field")

    assert exc_info.value.field == "json_field"
    assert exc_info.value.field_value == '{"name": "John"'
    assert "Failed to load JSON from field `json_field`" in str(exc_info.value)


def test_parse_json_complex_nested_structure():
    """Test parsing a complex nested JSON structure"""
    function = ParseJsonFunction()
    json_str = """{
        "users": [
            {"id": 1, "name": "Alice", "tags": ["admin", "user"]},
            {"id": 2, "name": "Bob", "tags": ["user"]}
        ],
        "metadata": {
            "count": 2,
            "timestamp": 1234567890
        }
    }"""
    data = {"json_field": json_str}
    result = function.execute(data=data, field="json_field")

    assert result["users"][0]["id"] == 1
    assert result["users"][0]["name"] == "Alice"
    assert result["users"][0]["tags"] == ["admin", "user"]
    assert result["metadata"]["count"] == 2
    assert result["metadata"]["timestamp"] == 1234567890


# Edge case tests
def test_parse_json_field_value_none():
    """Test that None as field value silently ignores and returns data unchanged"""
    function = ParseJsonFunction()
    data = {"json_field": None, "other_field": "value"}

    result = function.execute(data=data, field="json_field")

    # Should return data unchanged when field is None
    assert result == data
    assert "json_field" in result
    assert result["json_field"] is None


def test_parse_json_field_value_none_in_place():
    """Test that None as field value silently ignores even with in_place=True"""
    function = ParseJsonFunction()
    data = {"json_field": None, "other_field": "preserved"}

    result = function.execute(data=data, field="json_field", in_place=True)

    # Should return data unchanged when field is None
    assert result == data
    assert result["json_field"] is None
    assert result["other_field"] == "preserved"


def test_parse_json_very_large_string():
    """Test parsing JSON with a very large string value"""
    function = ParseJsonFunction()
    large_string = "x" * 10000
    data = {"json_field": f'{{"large_data": "{large_string}"}}'}
    result = function.execute(data=data, field="json_field")

    assert result["large_data"] == large_string
    assert len(result["large_data"]) == 10000


def test_parse_json_very_large_string_in_place():
    """Test parsing JSON with a very large string value in place"""
    function = ParseJsonFunction()
    large_string = "x" * 10000
    data = {"json_field": f'{{"large_data": "{large_string}"}}', "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"]["large_data"] == large_string
    assert len(result["json_field"]["large_data"]) == 10000
    assert result["other_field"] == "preserved"


def test_parse_json_with_control_characters():
    """Test parsing JSON with control characters (tab, newline, etc.)"""
    function = ParseJsonFunction()
    # JSON with tab, newline, carriage return
    data = {"json_field": '{"text": "Line 1\\nLine 2\\tTabbed\\rReturn"}'}
    result = function.execute(data=data, field="json_field")

    assert result["text"] == "Line 1\nLine 2\tTabbed\rReturn"


def test_parse_json_with_control_characters_in_place():
    """Test parsing JSON with control characters in place"""
    function = ParseJsonFunction()
    data = {
        "json_field": '{"text": "Line 1\\nLine 2\\tTabbed\\rReturn"}',
        "other_field": "preserved",
    }
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"]["text"] == "Line 1\nLine 2\tTabbed\rReturn"
    assert result["other_field"] == "preserved"


def test_parse_json_with_special_unicode_sequences():
    """Test parsing JSON with special unicode sequences (zero-width, combining characters)"""
    function = ParseJsonFunction()
    # Zero-width space, combining characters, RTL markers
    data = {"json_field": '{"text": "Hello\\u200B\\u0301\\u200FWorld"}'}
    result = function.execute(data=data, field="json_field")

    assert "text" in result
    assert isinstance(result["text"], str)


def test_parse_json_with_special_unicode_sequences_in_place():
    """Test parsing JSON with special unicode sequences in place"""
    function = ParseJsonFunction()
    data = {"json_field": '{"text": "Hello\\u200B\\u0301\\u200FWorld"}', "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert "text" in result["json_field"]
    assert isinstance(result["json_field"]["text"], str)
    assert result["other_field"] == "preserved"


def test_parse_json_with_numeric_string_keys():
    """Test parsing JSON with numeric string keys"""
    function = ParseJsonFunction()
    data = {"json_field": '{"123": "numeric_key", "0": "zero_key"}'}
    result = function.execute(data=data, field="json_field")

    assert result["123"] == "numeric_key"
    assert result["0"] == "zero_key"


def test_parse_json_with_numeric_string_keys_in_place():
    """Test parsing JSON with numeric string keys in place"""
    function = ParseJsonFunction()
    data = {"json_field": '{"123": "numeric_key", "0": "zero_key"}', "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"]["123"] == "numeric_key"
    assert result["json_field"]["0"] == "zero_key"
    assert result["other_field"] == "preserved"


def test_parse_json_with_very_long_field_names():
    """Test parsing JSON with very long field names"""
    function = ParseJsonFunction()
    long_field_name = "a" * 1000
    data = {"json_field": f'{{"{long_field_name}": "value"}}'}
    result = function.execute(data=data, field="json_field")

    assert result[long_field_name] == "value"
    assert len(list(result.keys())[0]) == 1000


def test_parse_json_with_very_long_field_names_in_place():
    """Test parsing JSON with very long field names in place"""
    function = ParseJsonFunction()
    long_field_name = "a" * 1000
    data = {"json_field": f'{{"{long_field_name}": "value"}}', "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"][long_field_name] == "value"
    assert len(list(result["json_field"].keys())[0]) == 1000
    assert result["other_field"] == "preserved"


# Tests for in_place=True functionality
def test_parse_json_in_place_simple_object():
    """Test parsing a simple JSON object in place"""
    function = ParseJsonFunction()
    data = {"json_field": '{"name": "John", "age": 30}', "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data  # Should return the same dict object
    assert result["json_field"] == {"name": "John", "age": 30}
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_nested_object():
    """Test parsing a nested JSON object in place"""
    function = ParseJsonFunction()
    data = {
        "json_field": '{"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}}',
        "other_field": "preserved",
    }
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}}
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_array():
    """Test parsing a JSON array in place"""
    function = ParseJsonFunction()
    data = {"json_field": '[1, 2, 3, "four", true, null]', "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == [1, 2, 3, "four", True, None]
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_array_of_objects():
    """Test parsing a JSON array of objects in place"""
    function = ParseJsonFunction()
    data = {
        "json_field": '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]',
        "other_field": "preserved",
    }
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_string():
    """Test parsing a JSON string in place"""
    function = ParseJsonFunction()
    data = {"json_field": '"Hello, World!"', "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == "Hello, World!"
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_number():
    """Test parsing a JSON number in place"""
    function = ParseJsonFunction()
    data = {"json_field": "42", "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == 42
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_float():
    """Test parsing a JSON float in place"""
    function = ParseJsonFunction()
    data = {"json_field": "3.14159", "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == 3.14159
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_boolean_true():
    """Test parsing a JSON boolean true in place"""
    function = ParseJsonFunction()
    data = {"json_field": "true", "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] is True
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_boolean_false():
    """Test parsing a JSON boolean false in place"""
    function = ParseJsonFunction()
    data = {"json_field": "false", "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] is False
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_null():
    """Test parsing a JSON null in place"""
    function = ParseJsonFunction()
    data = {"json_field": "null", "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] is None
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_empty_object():
    """Test parsing an empty JSON object in place"""
    function = ParseJsonFunction()
    data = {"json_field": "{}", "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == {}
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_empty_array():
    """Test parsing an empty JSON array in place"""
    function = ParseJsonFunction()
    data = {"json_field": "[]", "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == []
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_with_unicode():
    """Test parsing JSON with unicode characters in place"""
    function = ParseJsonFunction()
    data = {"json_field": '{"message": "Hello 世界", "emoji": "🎉"}', "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == {"message": "Hello 世界", "emoji": "🎉"}
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_with_escaped_characters():
    """Test parsing JSON with escaped characters in place"""
    function = ParseJsonFunction()
    data = {
        "json_field": '{"path": "C:\\\\Users\\\\test", "quote": "He said \\"Hello\\""}',
        "other_field": "preserved",
    }
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"] == {"path": "C:\\Users\\test", "quote": 'He said "Hello"'}
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_complex_nested_structure():
    """Test parsing a complex nested JSON structure in place"""
    function = ParseJsonFunction()
    json_str = """{
        "users": [
            {"id": 1, "name": "Alice", "tags": ["admin", "user"]},
            {"id": 2, "name": "Bob", "tags": ["user"]}
        ],
        "metadata": {
            "count": 2,
            "timestamp": 1234567890
        }
    }"""
    data = {"json_field": json_str, "other_field": "preserved"}
    result = function.execute(data=data, field="json_field", in_place=True)

    assert result is data
    assert result["json_field"]["users"][0]["id"] == 1
    assert result["json_field"]["users"][0]["name"] == "Alice"
    assert result["json_field"]["users"][0]["tags"] == ["admin", "user"]
    assert result["json_field"]["metadata"]["count"] == 2
    assert result["json_field"]["metadata"]["timestamp"] == 1234567890
    assert result["other_field"] == "preserved"


def test_parse_json_in_place_invalid_json():
    """Test that invalid JSON raises ParseJsonFunctionError even with in_place=True"""
    function = ParseJsonFunction()
    data = {"json_field": '{"name": "John", "age": }', "other_field": "preserved"}

    with pytest.raises(ParseJsonFunctionError) as exc_info:
        function.execute(data=data, field="json_field", in_place=True)

    assert exc_info.value.field == "json_field"
    assert exc_info.value.field_value == '{"name": "John", "age": }'
    assert "Failed to load JSON from field `json_field`" in str(exc_info.value)
    # Original data should remain unchanged
    assert data["json_field"] == '{"name": "John", "age": }'
    assert data["other_field"] == "preserved"


def test_parse_json_in_place_missing_field():
    """Test missing field silently ignores with in_place=True"""
    function = ParseJsonFunction()
    data = {"other_field": "value"}

    result = function.execute(data=data, field="json_field", in_place=True)

    # Should return data unchanged when field is not found
    assert result == data
    assert "other_field" in result


def test_parse_json_with_nested_path():
    """Test parse_json with nested field path"""
    function = ParseJsonFunction()
    data = {"event": {"raw": '{"name": "John", "age": 30}'}, "other": "value"}
    result = function.execute(data=data, field="event.raw", in_place=True)

    assert isinstance(result["event"]["raw"], dict)
    assert result["event"]["raw"]["name"] == "John"
    assert result["event"]["raw"]["age"] == 30
    assert result["other"] == "value"


def test_parse_json_with_deeply_nested_path():
    """Test parse_json with deeply nested field path"""
    function = ParseJsonFunction()
    data = {
        "level1": {
            "level2": {
                "json_field": '{"key": "value"}',
            },
        },
    }
    result = function.execute(data=data, field="level1.level2.json_field", in_place=True)

    assert isinstance(result["level1"]["level2"]["json_field"], dict)
    assert result["level1"]["level2"]["json_field"]["key"] == "value"


def test_parse_json_nested_path_missing():
    """Test parse_json with missing nested path silently ignores"""
    function = ParseJsonFunction()
    data = {"user": {"name": "John"}}
    result = function.execute(data=data, field="user.missing", in_place=True)

    # Should return data unchanged when nested path is not found
    assert result == data
    assert result["user"]["name"] == "John"

import pytest

from schema_parser.functions.extract import ExtractFunction


def test_extract_basic():
    """Test extracting a nested dictionary"""
    function = ExtractFunction()
    data = {"user": {"user_name": "test", "user_id": "1"}, "some_field": "some_value"}
    result = function.execute(data=data, field="user")

    assert result == {"user_name": "test", "user_id": "1", "some_field": "some_value"}
    assert "user" not in result


def test_extract_with_multiple_fields():
    """Test extracting when parent has multiple fields"""
    function = ExtractFunction()
    data = {
        "user": {"name": "John", "age": 30},
        "metadata": {"source": "api", "version": "1.0"},
        "other_field": "preserved",
    }
    result = function.execute(data=data, field="user")

    assert result["name"] == "John"
    assert result["age"] == 30
    assert result["metadata"] == {"source": "api", "version": "1.0"}
    assert result["other_field"] == "preserved"
    assert "user" not in result


def test_extract_preserves_other_fields():
    """Test that other fields are preserved after extraction"""
    function = ExtractFunction()
    data = {
        "nested": {"field1": "value1", "field2": "value2"},
        "top_level": "preserved",
        "another": "also_preserved",
    }
    result = function.execute(data=data, field="nested")

    assert result["field1"] == "value1"
    assert result["field2"] == "value2"
    assert result["top_level"] == "preserved"
    assert result["another"] == "also_preserved"
    assert "nested" not in result


def test_extract_with_empty_nested_dict():
    """Test that extracting an empty nested dictionary extracts it (removes the field)"""
    function = ExtractFunction()
    data = {"empty": {}, "other": "value"}
    result = function.execute(data=data, field="empty")

    # Empty dict is valid and should be extracted (field removed, nothing merged)
    assert result == {"other": "value"}
    assert "empty" not in result


def test_extract_with_nested_dict_containing_multiple_keys():
    """Test extracting a nested dictionary with many keys"""
    function = ExtractFunction()
    data = {
        "user": {
            "id": "123",
            "name": "Alice",
            "email": "alice@example.com",
            "age": 25,
            "city": "NYC",
        },
        "timestamp": "2024-01-01",
    }
    result = function.execute(data=data, field="user")

    assert result["id"] == "123"
    assert result["name"] == "Alice"
    assert result["email"] == "alice@example.com"
    assert result["age"] == 25
    assert result["city"] == "NYC"
    assert result["timestamp"] == "2024-01-01"
    assert "user" not in result


def test_extract_field_not_found():
    """Test that extracting a non-existent field silently ignores and returns data unchanged"""
    function = ExtractFunction()
    data = {"other_field": "value"}

    result = function.execute(data=data, field="nonexistent")

    # Should return data unchanged when field is not found
    assert result == data
    assert "other_field" in result


def test_extract_field_is_none():
    """Test that extracting a field with None value silently ignores and returns data unchanged"""
    function = ExtractFunction()
    data = {"field": None, "other_field": "value"}

    result = function.execute(data=data, field="field")

    # Should return data unchanged when field is None
    assert result == data
    assert "field" in result
    assert result["field"] is None


def test_extract_field_is_empty_string():
    """Test that extracting a field with empty string silently ignores and returns data unchanged"""
    function = ExtractFunction()
    data = {"field": "", "other_field": "value"}

    result = function.execute(data=data, field="field")

    # Should return data unchanged when field is empty string
    assert result == data
    assert "field" in result
    assert result["field"] == ""


def test_extract_field_is_empty_list():
    """Test that extracting a field with empty list silently ignores and returns data unchanged"""
    function = ExtractFunction()
    data = {"field": [], "other_field": "value"}

    result = function.execute(data=data, field="field")

    # Empty list is treated as empty and should be ignored
    assert result == data
    assert "field" in result
    assert result["field"] == []


def test_extract_field_is_zero():
    """Test that extracting a field with zero raises error (zero is not empty, not a dict)"""
    function = ExtractFunction()
    data = {"field": 0, "other_field": "value"}

    # Zero is not empty, so it should try to extract it and raise error (not a dict)
    with pytest.raises(ValueError) as exc_info:
        function.execute(data=data, field="field")

    assert "does not contain a dictionary" in str(exc_info.value)


def test_extract_field_is_false():
    """Test that extracting a field with False raises error (False is not empty, not a dict)"""
    function = ExtractFunction()
    data = {"field": False, "other_field": "value"}

    # False is not empty, so it should try to extract it and raise error (not a dict)
    with pytest.raises(ValueError) as exc_info:
        function.execute(data=data, field="field")

    assert "does not contain a dictionary" in str(exc_info.value)


def test_extract_field_not_a_dict():
    """Test that extracting a field that is not a dictionary raises an error"""
    function = ExtractFunction()
    data = {"user": "not_a_dict", "other": "value"}

    with pytest.raises(ValueError) as exc_info:
        function.execute(data=data, field="user")

    assert "does not contain a dictionary" in str(exc_info.value)


def test_extract_field_is_list():
    """Test that extracting a field that is a list raises an error"""
    function = ExtractFunction()
    data = {"user": [1, 2, 3], "other": "value"}

    with pytest.raises(ValueError) as exc_info:
        function.execute(data=data, field="user")

    assert "does not contain a dictionary" in str(exc_info.value)


def test_extract_field_is_string():
    """Test that extracting a field that is a string raises an error"""
    function = ExtractFunction()
    data = {"user": "string_value", "other": "value"}

    with pytest.raises(ValueError) as exc_info:
        function.execute(data=data, field="user")

    assert "does not contain a dictionary" in str(exc_info.value)


def test_extract_field_is_number():
    """Test that extracting a field that is a number raises an error"""
    function = ExtractFunction()
    data = {"user": 123, "other": "value"}

    with pytest.raises(ValueError) as exc_info:
        function.execute(data=data, field="user")

    assert "does not contain a dictionary" in str(exc_info.value)


def test_extract_with_overlapping_keys():
    """Test extracting when nested dict and parent have overlapping keys"""
    function = ExtractFunction()
    data = {
        "nested": {"field1": "nested_value1", "field2": "nested_value2"},
        "field1": "parent_value1",
        "field3": "parent_value3",
    }
    result = function.execute(data=data, field="nested")

    # The nested dict's values should overwrite parent values
    assert result["field1"] == "nested_value1"
    assert result["field2"] == "nested_value2"
    assert result["field3"] == "parent_value3"
    assert "nested" not in result


def test_extract_modifies_original_data():
    """Test that extract modifies the data dictionary in place"""
    function = ExtractFunction()
    data = {"user": {"name": "John"}, "other": "value"}
    original_data = data.copy()

    result = function.execute(data=data, field="user")

    # The result should be the same object reference
    assert result is data
    # Original data should be modified
    assert data != original_data
    assert "user" not in data
    assert "name" in data


def test_extract_with_nested_path():
    """Test extracting a nested dictionary using dot-separated path"""
    function = ExtractFunction()
    data = {
        "winlog": {
            "event_data": {"LogonGuid": "test123", "IntegrityLevel": "System"},
            "other": "preserved",
        },
        "other_field": "value",
    }
    result = function.execute(data=data, field="winlog.event_data")

    assert result["LogonGuid"] == "test123"
    assert result["IntegrityLevel"] == "System"
    assert result["other_field"] == "value"
    assert result["winlog"]["other"] == "preserved"
    assert "event_data" not in result["winlog"]


def test_extract_with_deeply_nested_path():
    """Test extracting from a deeply nested path"""
    function = ExtractFunction()
    data = {
        "level1": {
            "level2": {
                "level3": {"value": "extracted", "other": "preserved"},
            },
        },
        "top": "level",
    }
    result = function.execute(data=data, field="level1.level2.level3")

    assert result["value"] == "extracted"
    assert result["top"] == "level"
    assert result["level1"]["level2"] == {}


def test_extract_nested_path_not_found():
    """Test that extracting a non-existent nested path silently ignores"""
    function = ExtractFunction()
    data = {"user": {"name": "John"}}

    result = function.execute(data=data, field="user.nonexistent")

    # Should silently ignore and return data unchanged
    assert result == data
    assert "user" in result

from schema_parser.functions.drop import DropFunction


def test_drop_basic():
    """Test basic drop operation"""
    function = DropFunction()
    data = {"field1": "value1", "field2": "value2", "field3": "value3"}
    result = function.execute(data=data, fields="field2")

    assert "field2" not in result
    assert "field1" in result
    assert "field3" in result


def test_drop_multiple_fields():
    """Test dropping multiple fields"""
    function = DropFunction()
    data = {"field1": "value1", "field2": "value2", "field3": "value3", "field4": "value4"}
    result = function.execute(data=data, fields="field1,field3")

    assert "field1" not in result
    assert "field3" not in result
    assert "field2" in result
    assert "field4" in result


def test_drop_with_nested_path():
    """Test dropping a nested field"""
    function = DropFunction()
    data = {"user": {"name": "John", "age": 30}, "other": "value"}
    result = function.execute(data=data, fields="user.name")

    assert "name" not in result["user"]
    assert result["user"]["age"] == 30
    assert result["other"] == "value"


def test_drop_with_deeply_nested_path():
    """Test dropping a deeply nested field"""
    function = DropFunction()
    data = {
        "level1": {
            "level2": {
                "level3": {"value": "found", "other": "preserved"},
            },
        },
    }
    result = function.execute(data=data, fields="level1.level2.level3.value")

    assert "value" not in result["level1"]["level2"]["level3"]
    assert result["level1"]["level2"]["level3"]["other"] == "preserved"


def test_drop_missing_field():
    """Test that dropping a missing field silently ignores it"""
    function = DropFunction()
    data = {"field1": "value1"}
    result = function.execute(data=data, fields="missing")

    # Should not raise error, just ignore missing field
    assert result == data


def test_drop_missing_nested_path():
    """Test that dropping a missing nested path silently ignores it"""
    function = DropFunction()
    data = {"user": {"name": "John"}}
    result = function.execute(data=data, fields="user.missing")

    # Should not raise error, just ignore missing path
    assert result == data


def test_drop_multiple_with_nested_paths():
    """Test dropping multiple fields including nested paths"""
    function = DropFunction()
    data = {
        "top": "value",
        "user": {"name": "John", "age": 30},
        "other": "preserved",
    }
    result = function.execute(data=data, fields="top,user.name")

    assert "top" not in result
    assert "name" not in result["user"]
    assert result["user"]["age"] == 30
    assert result["other"] == "preserved"

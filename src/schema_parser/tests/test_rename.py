import pytest

from schema_parser.functions.rename import RenameFunction


def test_rename_basic():
    """Test basic rename operation"""
    function = RenameFunction()
    data = {"old_field": "value", "other": "preserved"}
    result = function.execute(data=data, from_field="old_field", to_field="new_field")

    assert "old_field" not in result
    assert result["new_field"] == "value"
    assert result["other"] == "preserved"


def test_rename_with_nested_from_path():
    """Test renaming from a nested path"""
    function = RenameFunction()
    data = {"user": {"name": "John", "age": 30}, "other": "value"}
    result = function.execute(data=data, from_field="user.name", to_field="user_name")

    assert "name" not in result["user"]
    assert result["user_name"] == "John"
    assert result["user"]["age"] == 30
    assert result["other"] == "value"


def test_rename_with_nested_to_path():
    """Test renaming to a nested path"""
    function = RenameFunction()
    data = {"name": "John", "other": "value"}
    result = function.execute(data=data, from_field="name", to_field="user.name")

    assert "name" not in result
    assert result["user"]["name"] == "John"
    assert result["other"] == "value"


def test_rename_with_nested_from_and_to_paths():
    """Test renaming from nested path to nested path"""
    function = RenameFunction()
    data = {"user": {"profile": {"name": "John"}}, "other": "value"}
    result = function.execute(data=data, from_field="user.profile.name", to_field="user.name")

    # Profile dict becomes empty but still exists
    assert result["user"]["profile"] == {}
    assert result["user"]["name"] == "John"
    assert result["other"] == "value"


def test_rename_missing_field():
    """Test that renaming a missing field raises an error"""
    function = RenameFunction()
    data = {"other": "value"}

    with pytest.raises(ValueError) as exc_info:
        function.execute(data=data, from_field="missing", to_field="new")

    assert "Field missing not found in data" in str(exc_info.value)


def test_rename_missing_nested_path():
    """Test that renaming a missing nested path raises an error"""
    function = RenameFunction()
    data = {"user": {"name": "John"}}

    with pytest.raises(ValueError) as exc_info:
        function.execute(data=data, from_field="user.missing", to_field="new")

    assert "Field user.missing not found in data" in str(exc_info.value)


def test_rename_creates_intermediate_dicts():
    """Test that renaming to nested path creates intermediate dictionaries"""
    function = RenameFunction()
    data = {"value": "test", "other": "preserved"}
    result = function.execute(data=data, from_field="value", to_field="nested.deep.value")

    assert "value" not in result
    assert result["nested"]["deep"]["value"] == "test"
    assert result["other"] == "preserved"

from schema_parser.functions.set import SetFunction


def test_set_basic():
    """Test basic set operation"""
    function = SetFunction()
    data = {"existing": "value"}
    result = function.execute(data=data, field="new_field", value="new_value")

    assert result["new_field"] == "new_value"
    assert result["existing"] == "value"


def test_set_overwrites_existing():
    """Test that set overwrites existing values"""
    function = SetFunction()
    data = {"field": "old_value"}
    result = function.execute(data=data, field="field", value="new_value")

    assert result["field"] == "new_value"


def test_set_with_nested_path():
    """Test setting a value in a nested path"""
    function = SetFunction()
    data = {"user": {"name": "John"}, "other": "value"}
    result = function.execute(data=data, field="user.age", value=30)

    assert result["user"]["age"] == 30
    assert result["user"]["name"] == "John"
    assert result["other"] == "value"


def test_set_creates_intermediate_dicts():
    """Test that set creates intermediate dictionaries if they don't exist"""
    function = SetFunction()
    data = {"other": "value"}
    result = function.execute(data=data, field="nested.deep.value", value="test")

    assert result["nested"]["deep"]["value"] == "test"
    assert result["other"] == "value"


def test_set_overwrites_non_dict():
    """Test that set overwrites non-dict values with dicts when needed"""
    function = SetFunction()
    data = {"user": "not_a_dict"}
    result = function.execute(data=data, field="user.name", value="John")

    assert isinstance(result["user"], dict)
    assert result["user"]["name"] == "John"


def test_set_with_deeply_nested_path():
    """Test setting a value in a deeply nested path"""
    function = SetFunction()
    data = {}
    result = function.execute(data=data, field="level1.level2.level3.value", value="found")

    assert result["level1"]["level2"]["level3"]["value"] == "found"

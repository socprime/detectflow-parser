from schema_parser.core.utils import get_value


def test_get_value_simple_key():
    """Test getting a value with a simple key (no dots)"""
    data = {"name": "John", "age": 30}
    assert get_value(data, "name") == "John"
    assert get_value(data, "age") == 30


def test_get_value_nested_path():
    """Test getting a value with a nested path"""
    data = {"user": {"name": "John", "age": 30}}
    assert get_value(data, "user.name") == "John"
    assert get_value(data, "user.age") == 30


def test_get_value_deeply_nested_path():
    """Test getting a value from a deeply nested path"""
    data = {
        "level1": {
            "level2": {
                "level3": {"value": "found", "other": "data"},
            },
        },
    }
    assert get_value(data, "level1.level2.level3.value") == "found"
    assert get_value(data, "level1.level2.level3.other") == "data"


def test_get_value_missing_simple_key():
    """Test getting a missing simple key returns None"""
    data = {"name": "John"}
    assert get_value(data, "missing") is None


def test_get_value_missing_nested_path():
    """Test getting a missing nested path returns None"""
    data = {"user": {"name": "John"}}
    assert get_value(data, "user.missing") is None
    assert get_value(data, "missing.field") is None


def test_get_value_invalid_intermediate_path():
    """Test getting a value when intermediate path is not a dict"""
    data = {"user": "not_a_dict"}
    assert get_value(data, "user.field") is None


def test_get_value_invalid_path_type():
    """Test getting a value when path goes through non-dict value"""
    data = {"user": {"name": "John", "age": 30}}
    # If we try to access user.name.field, it should return None since "John" is not a dict
    assert get_value(data, "user.name.field") is None


def test_get_value_with_none_value():
    """Test getting a None value"""
    data = {"field": None, "other": "value"}
    assert get_value(data, "field") is None
    assert get_value(data, "other") == "value"


def test_get_value_with_empty_string():
    """Test getting an empty string value"""
    data = {"field": "", "other": "value"}
    assert get_value(data, "field") == ""
    assert get_value(data, "other") == "value"


def test_get_value_with_empty_dict():
    """Test getting an empty dict value"""
    data = {"field": {}, "other": "value"}
    assert get_value(data, "field") == {}
    assert get_value(data, "other") == "value"


def test_get_value_with_empty_list():
    """Test getting an empty list value"""
    data = {"field": [], "other": "value"}
    assert get_value(data, "field") == []
    assert get_value(data, "other") == "value"


def test_get_value_with_nested_none():
    """Test getting a None value from nested path"""
    data = {"user": {"name": None, "age": 30}}
    assert get_value(data, "user.name") is None
    assert get_value(data, "user.age") == 30


def test_get_value_with_numeric_values():
    """Test getting numeric values"""
    data = {"count": 0, "price": 99.99, "negative": -5}
    assert get_value(data, "count") == 0
    assert get_value(data, "price") == 99.99
    assert get_value(data, "negative") == -5


def test_get_value_with_boolean_values():
    """Test getting boolean values"""
    data = {"active": True, "deleted": False}
    assert get_value(data, "active") is True
    assert get_value(data, "deleted") is False


def test_get_value_with_list_values():
    """Test getting list values"""
    data = {"items": [1, 2, 3], "tags": ["a", "b"]}
    assert get_value(data, "items") == [1, 2, 3]
    assert get_value(data, "tags") == ["a", "b"]


def test_get_value_with_dict_values():
    """Test getting dict values"""
    data = {"metadata": {"version": "1.0", "author": "John"}}
    assert get_value(data, "metadata") == {"version": "1.0", "author": "John"}
    assert get_value(data, "metadata.version") == "1.0"
    assert get_value(data, "metadata.author") == "John"


def test_get_value_path_with_dots_in_key():
    """Test that path with dots prioritizes simple key if it exists"""
    data = {"user": {"name": "John"}, "user.name": "different"}
    # If "user.name" exists as a simple key, it returns that value first
    assert get_value(data, "user.name") == "different"
    # If the simple key doesn't exist, it treats it as nested path
    data2 = {"user": {"name": "John"}}
    assert get_value(data2, "user.name") == "John"


def test_get_value_empty_path():
    """Test getting value with empty path"""
    data = {"field": "value"}
    # Empty path should return None
    assert get_value(data, "") is None


def test_get_value_complex_nested_structure():
    """Test getting values from a complex nested structure"""
    data = {
        "users": [
            {"name": "John", "settings": {"theme": "dark"}},
        ],
        "config": {
            "app": {"name": "MyApp", "version": "1.0"},
            "db": {"host": "localhost", "port": 5432},
        },
    }
    assert get_value(data, "config.app.name") == "MyApp"
    assert get_value(data, "config.app.version") == "1.0"
    assert get_value(data, "config.db.host") == "localhost"
    assert get_value(data, "config.db.port") == 5432
    # Lists are not traversed, so this should return None
    assert get_value(data, "users.0.name") is None


def test_get_value_single_dot_path():
    """Test getting value with single dot (edge case)"""
    data = {"a": {"b": "value"}}
    assert get_value(data, "a.b") == "value"


def test_get_value_multiple_dots_path():
    """Test getting value with multiple dots"""
    data = {"a": {"b": {"c": {"d": "value"}}}}
    assert get_value(data, "a.b.c.d") == "value"


def test_get_value_path_ends_with_dot():
    """Test getting value when path ends with dot"""
    data = {"user": {"name": "John"}}
    # Path ending with dot should return None (invalid path)
    assert get_value(data, "user.") is None
    assert get_value(data, "user.name.") is None


# Tests for set_value
def test_set_value_simple_key():
    """Test setting a value with a simple key (no dots)"""
    data = {"name": "John"}
    from schema_parser.core.utils import set_value

    set_value(data, "age", 30)
    assert data["age"] == 30
    assert data["name"] == "John"


def test_set_value_nested_path():
    """Test setting a value with a nested path"""
    data = {"user": {"name": "John"}}
    from schema_parser.core.utils import set_value

    set_value(data, "user.age", 30)
    assert data["user"]["age"] == 30
    assert data["user"]["name"] == "John"


def test_set_value_deeply_nested_path():
    """Test setting a value in a deeply nested path"""
    data = {"level1": {"level2": {}}}
    from schema_parser.core.utils import set_value

    set_value(data, "level1.level2.level3.value", "found")
    assert data["level1"]["level2"]["level3"]["value"] == "found"


def test_set_value_creates_intermediate_dicts():
    """Test that set_value creates intermediate dictionaries if they don't exist"""
    data = {}
    from schema_parser.core.utils import set_value

    set_value(data, "a.b.c", "value")
    assert data["a"]["b"]["c"] == "value"


def test_set_value_overwrites_existing():
    """Test that set_value overwrites existing values"""
    data = {"user": {"name": "John"}}
    from schema_parser.core.utils import set_value

    set_value(data, "user.name", "Jane")
    assert data["user"]["name"] == "Jane"


def test_set_value_overwrites_non_dict():
    """Test that set_value overwrites non-dict values with dicts when needed"""
    data = {"user": "not_a_dict"}
    from schema_parser.core.utils import set_value

    set_value(data, "user.name", "John")
    assert isinstance(data["user"], dict)
    assert data["user"]["name"] == "John"


# Tests for delete_value
def test_delete_value_simple_key():
    """Test deleting a value with a simple key (no dots)"""
    data = {"name": "John", "age": 30}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "age")
    assert deleted == 30
    assert "age" not in data
    assert "name" in data


def test_delete_value_nested_path():
    """Test deleting a value with a nested path"""
    data = {"user": {"name": "John", "age": 30}}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "user.age")
    assert deleted == 30
    assert "age" not in data["user"]
    assert "name" in data["user"]


def test_delete_value_deeply_nested_path():
    """Test deleting a value from a deeply nested path"""
    data = {"level1": {"level2": {"level3": {"value": "found"}}}}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "level1.level2.level3.value")
    assert deleted == "found"
    assert "value" not in data["level1"]["level2"]["level3"]


def test_delete_value_missing_simple_key():
    """Test deleting a missing simple key returns None"""
    data = {"name": "John"}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "missing")
    assert deleted is None
    assert "name" in data


def test_delete_value_missing_nested_path():
    """Test deleting a missing nested path returns None"""
    data = {"user": {"name": "John"}}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "user.missing")
    assert deleted is None
    assert "user" in data
    assert "name" in data["user"]


def test_delete_value_invalid_intermediate_path():
    """Test deleting when intermediate path is not a dict"""
    data = {"user": "not_a_dict"}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "user.field")
    assert deleted is None
    assert data["user"] == "not_a_dict"


def test_delete_value_removes_empty_dicts():
    """Test that deleting the last value in a nested dict leaves the structure"""
    data = {"user": {"profile": {"name": "John"}}}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "user.profile.name")
    assert deleted == "John"
    assert "user" in data
    assert "profile" in data["user"]
    assert data["user"]["profile"] == {}


def test_set_value_replaces_direct_key():
    """Test that set_value replaces a direct key that conflicts with nested path"""
    data = {"a.b": "old_value", "other": "preserved"}
    from schema_parser.core.utils import set_value

    set_value(data, "a.b", "new_value")
    assert "a.b" not in data
    assert data["a"]["b"] == "new_value"
    assert data["other"] == "preserved"


def test_set_value_replaces_direct_key_with_nested_structure():
    """Test that set_value replaces a direct key and creates nested structure"""
    data = {"user.name": "John", "other": "value"}
    from schema_parser.core.utils import set_value

    set_value(data, "user.name", "Jane")
    assert "user.name" not in data
    assert data["user"]["name"] == "Jane"
    assert data["other"] == "value"


def test_delete_value_deletes_direct_key_first():
    """Test that delete_value deletes direct key if it exists instead of nested path"""
    data = {"a.b": "direct_value", "other": "preserved"}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "a.b")
    assert deleted == "direct_value"
    assert "a.b" not in data
    assert data["other"] == "preserved"


def test_delete_value_falls_back_to_nested_if_no_direct_key():
    """Test that delete_value uses nested path if direct key doesn't exist"""
    data = {"a": {"b": "nested_value"}, "other": "preserved"}
    from schema_parser.core.utils import delete_value

    deleted = delete_value(data, "a.b")
    assert deleted == "nested_value"
    assert "b" not in data["a"]
    assert data["other"] == "preserved"


def test_set_value_with_complex_direct_key():
    """Test set_value with a complex direct key name"""
    data = {"level1.level2.level3": "direct", "other": "value"}
    from schema_parser.core.utils import set_value

    set_value(data, "level1.level2.level3", "nested")
    assert "level1.level2.level3" not in data
    assert data["level1"]["level2"]["level3"] == "nested"
    assert data["other"] == "value"

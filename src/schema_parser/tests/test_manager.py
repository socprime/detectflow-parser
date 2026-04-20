import pytest

from schema_parser.manager import ParserManager


def parser_step(function_name, **args):
    return {"function_name": function_name, "args": args}


class TestParserManagerDeepCopy:
    """Tests to ensure original event is not modified when using configured_parser"""

    def test_original_event_not_modified_on_success(self):
        """Test that original event is not modified when parsing succeeds"""
        manager = ParserManager()
        original_event = {
            "user": {"name": "John", "age": 30},
            "metadata": {"source": "api"},
        }

        parser_config = {
            "steps": [parser_step("extract", field="user")],
        }

        result = manager.configured_parser(original_event, parser_config)

        # Original event should be unchanged
        assert original_event == {
            "user": {"name": "John", "age": 30},
            "metadata": {"source": "api"},
        }
        # Result should be modified
        assert "user" not in result
        assert result["name"] == "John"
        assert result["age"] == 30

    def test_original_event_not_modified_on_error(self):
        """Test that original event is not modified when an error occurs"""
        manager = ParserManager()
        original_event = {
            "user": {"name": "John", "age": 30},
            "invalid_field": "not_a_dict",  # This will cause an error when extracted
            "metadata": {"source": "api"},
        }

        parser_config = {
            "steps": [
                parser_step("extract", field="invalid_field"),  # Will raise error - not a dict
            ],
        }

        # Extract will fail because invalid_field is not a dictionary
        with pytest.raises(ValueError):
            manager.configured_parser(original_event, parser_config)

        # Original event should still be unchanged
        assert original_event == {
            "user": {"name": "John", "age": 30},
            "invalid_field": "not_a_dict",
            "metadata": {"source": "api"},
        }

    def test_original_event_not_modified_with_nested_structures(self):
        """Test that nested structures in original event are not modified"""
        manager = ParserManager()
        original_event = {
            "data": {
                "nested": {"deep": {"value": "original"}},
                "list": [1, 2, 3],
            },
            "other": "preserved",
        }

        parser_config = {
            "steps": [parser_step("extract", field="data")],
        }

        result = manager.configured_parser(original_event, parser_config)

        # Original nested structure should be unchanged
        assert original_event["data"]["nested"]["deep"]["value"] == "original"
        assert original_event["data"]["list"] == [1, 2, 3]

        # Result should have extracted fields
        assert "data" not in result
        assert result["nested"]["deep"]["value"] == "original"

    def test_original_event_not_modified_with_multiple_functions(self):
        """Test that original event is not modified with multiple function calls"""
        manager = ParserManager()
        original_event = {
            "user": {"name": "John", "age": 30},
            "other": "value",
        }

        parser_config = {
            "steps": [
                parser_step("extract", field="user"),
                parser_step("set", field="status", value="active"),
            ],
        }

        result = manager.configured_parser(original_event, parser_config)

        # Original event should be unchanged
        assert original_event == {
            "user": {"name": "John", "age": 30},
            "other": "value",
        }

        # Result should be modified
        assert result["name"] == "John"
        assert result["age"] == 30
        assert result["status"] == "active"
        assert "user" not in result

    def test_original_event_not_modified_when_suppress_errors(self):
        """Test that original event is not modified when errors are suppressed"""
        manager = ParserManager()
        original_event = {
            "user": {"name": "John"},
            "invalid_field": "not_a_dict",  # This will cause an error when extracted
            "other": "value",
        }

        parser_config = {
            "steps": [
                parser_step("extract", field="invalid_field"),  # Will raise error - not a dict
            ],
        }

        result = manager.configured_parser(original_event, parser_config, suppress_errors=True)

        # Original event should be unchanged
        assert original_event == {
            "user": {"name": "John"},
            "invalid_field": "not_a_dict",
            "other": "value",
        }

        # Should return original event when error is suppressed
        assert result == original_event

    def test_deepcopy_preserves_nested_modifications(self):
        """Test that modifications to nested structures don't affect original"""
        manager = ParserManager()
        original_event = {
            "user": {
                "profile": {"name": "John", "settings": {"theme": "dark"}},
            },
            "metadata": {"version": "1.0"},
        }

        parser_config = {
            "steps": [parser_step("extract", field="user")],
        }

        result = manager.configured_parser(original_event, parser_config)

        # Modify the nested structure in result
        result["profile"]["settings"]["theme"] = "light"

        # Original should still have the original value
        assert original_event["user"]["profile"]["settings"]["theme"] == "dark"

    def test_deepcopy_with_lists(self):
        """Test that lists in nested structures are properly deep copied"""
        manager = ParserManager()
        original_event = {
            "data": {
                "items": [1, 2, 3],
                "nested": {"list": ["a", "b", "c"]},
            },
        }

        parser_config = {
            "steps": [parser_step("extract", field="data")],
        }

        result = manager.configured_parser(original_event, parser_config)

        # Modify list in result
        result["items"].append(4)
        result["nested"]["list"].append("d")

        # Original lists should be unchanged
        assert original_event["data"]["items"] == [1, 2, 3]
        assert original_event["data"]["nested"]["list"] == ["a", "b", "c"]

    def test_deepcopy_with_complex_nested_structure(self):
        """Test deepcopy with a complex nested structure"""
        manager = ParserManager()
        original_event = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "original",
                        "list": [{"nested": "dict"}],
                    },
                },
            },
            "simple": "value",
        }

        parser_config = {
            "steps": [parser_step("extract", field="level1")],
        }

        result = manager.configured_parser(original_event, parser_config)

        # Modify deeply nested structure
        result["level2"]["level3"]["value"] = "modified"
        result["level2"]["level3"]["list"][0]["nested"] = "changed"

        # Original should be unchanged
        assert original_event["level1"]["level2"]["level3"]["value"] == "original"
        assert original_event["level1"]["level2"]["level3"]["list"][0]["nested"] == "dict"

    def test_shallow_copy_bug_fixed(self):
        """
        Test that demonstrates the bug fix: with shallow copy, nested structures
        would be modified. With deepcopy, they remain unchanged even when errors occur.
        """
        manager = ParserManager()
        original_event = {
            "user": {
                "profile": {"name": "John", "settings": {"theme": "dark"}},
                "metadata": {"version": "1.0"},
            },
            "invalid_field": "not_a_dict",  # This will cause an error when extracted
        }

        # Extract will fail because invalid_field is not a dict
        parser_config = {
            "steps": [
                parser_step("extract", field="invalid_field"),  # Will fail - not a dict
            ],
        }

        with pytest.raises(ValueError):
            manager.configured_parser(original_event, parser_config)

        # Even though extract attempted to process the field and failed,
        # original event should be completely unchanged
        assert original_event == {
            "user": {
                "profile": {"name": "John", "settings": {"theme": "dark"}},
                "metadata": {"version": "1.0"},
            },
            "invalid_field": "not_a_dict",
        }
        assert original_event["user"]["profile"]["settings"]["theme"] == "dark"


class TestParserManagerFlatten:
    """Tests for the flatten parameter in configured_parser"""

    def test_flatten_false_keeps_nested_structure(self):
        """Test that flatten=False (default) keeps nested structure"""
        manager = ParserManager()
        event = {
            "user": {"name": "John", "age": 30},
            "metadata": {"source": "api"},
        }

        parser_config = {
            "steps": [],
        }

        result = manager.configured_parser(event, parser_config, flatten=False)

        # Result should maintain nested structure
        assert result == event
        assert isinstance(result["user"], dict)
        assert result["user"]["name"] == "John"

    def test_flatten_true_flattens_nested_structure(self):
        """Test that flatten=True flattens nested structure with dot notation"""
        manager = ParserManager()
        event = {
            "user": {"name": "John", "age": 30},
            "metadata": {"source": "api"},
        }

        parser_config = {
            "steps": [],
        }

        result = manager.configured_parser(event, parser_config, flatten=True)

        # Result should be flattened with dot notation
        assert "user.name" in result
        assert "user.age" in result
        assert "metadata.source" in result
        assert result["user.name"] == "John"
        assert result["user.age"] == 30
        assert result["metadata.source"] == "api"
        # Original nested keys should not exist
        assert "user" not in result
        assert "metadata" not in result

    def test_flatten_with_extract_function(self):
        """Test flattening after extract function"""
        manager = ParserManager()
        event = {
            "user": {"name": "John", "profile": {"theme": "dark"}},
            "other": "value",
        }

        parser_config = {
            "steps": [parser_step("extract", field="user")],
        }

        result = manager.configured_parser(event, parser_config, flatten=True)

        # After extract, user fields are at top level, then flattened
        assert "name" in result
        assert "profile.theme" in result
        assert "other" in result
        assert result["name"] == "John"
        assert result["profile.theme"] == "dark"
        assert result["other"] == "value"
        # Nested structures should be flattened
        assert "profile" not in result

    def test_flatten_with_multiple_functions(self):
        """Test flattening with multiple function steps"""
        manager = ParserManager()
        event = {
            "user": {"name": "John", "age": 30},
            "metadata": {"source": "api"},
        }

        parser_config = {
            "steps": [
                parser_step("extract", field="user"),
                parser_step("set", field="status", value="active"),
            ],
        }

        result = manager.configured_parser(event, parser_config, flatten=True)

        # After extract and set, all fields should be at top level and flattened
        assert "name" in result
        assert "age" in result
        assert "status" in result
        assert "metadata.source" in result
        assert result["name"] == "John"
        assert result["age"] == 30
        assert result["status"] == "active"
        assert result["metadata.source"] == "api"

    def test_flatten_with_deeply_nested_structure(self):
        """Test flattening with deeply nested structures"""
        manager = ParserManager()
        event = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep",
                        "nested": {"key": "value"},
                    },
                },
            },
            "simple": "value",
        }

        parser_config = {
            "steps": [],
        }

        result = manager.configured_parser(event, parser_config, flatten=True)

        # Deeply nested structure should be flattened
        assert "level1.level2.level3.value" in result
        assert "level1.level2.level3.nested.key" in result
        assert "simple" in result
        assert result["level1.level2.level3.value"] == "deep"
        assert result["level1.level2.level3.nested.key"] == "value"
        assert result["simple"] == "value"

    def test_flatten_with_no_nested_structure(self):
        """Test flattening with flat structure (should remain flat)"""
        manager = ParserManager()
        event = {
            "name": "John",
            "age": 30,
            "status": "active",
        }

        parser_config = {
            "steps": [],
        }

        result = manager.configured_parser(event, parser_config, flatten=True)

        # Flat structure should remain flat
        assert result == event
        assert result["name"] == "John"
        assert result["age"] == 30
        assert result["status"] == "active"

    def test_flatten_comparison(self):
        """Test comparison between flatten=True and flatten=False"""
        manager = ParserManager()
        event = {
            "user": {"name": "John", "profile": {"theme": "dark"}},
            "metadata": {"source": "api"},
        }

        parser_config = {
            "steps": [],
        }

        result_not_flattened = manager.configured_parser(event, parser_config, flatten=False)
        result_flattened = manager.configured_parser(event, parser_config, flatten=True)

        # Not flattened should maintain structure
        assert isinstance(result_not_flattened["user"], dict)
        assert result_not_flattened["user"]["name"] == "John"

        # Flattened should use dot notation
        assert "user.name" in result_flattened
        assert result_flattened["user.name"] == "John"
        assert "user" not in result_flattened

    def test_flatten_when_error_occurs(self):
        """Test that flatten is not applied when error occurs and suppress_errors=True"""
        manager = ParserManager()
        event = {
            "user": {"name": "John"},
            "invalid_field": "not_a_dict",
        }

        parser_config = {
            "steps": [
                parser_step("extract", field="invalid_field"),  # Will raise error
            ],
        }

        result = manager.configured_parser(event, parser_config, suppress_errors=True, flatten=True)

        # When error is suppressed, original event is returned (not flattened)
        assert result == event
        assert isinstance(result["user"], dict)
        assert "user.name" not in result

    def test_flatten_with_set_function_creating_nested(self):
        """Test flattening when set function creates nested structure"""
        manager = ParserManager()
        event = {
            "name": "John",
        }

        parser_config = {
            "steps": [parser_step("set", field="user.profile.theme", value="dark")],
        }

        result = manager.configured_parser(event, parser_config, flatten=True)

        # The nested structure created by set should be flattened
        assert "name" in result
        assert "user.profile.theme" in result
        assert result["name"] == "John"
        assert result["user.profile.theme"] == "dark"

    def test_flatten_preserves_original_event(self):
        """Test that flattening doesn't modify the original event"""
        manager = ParserManager()
        original_event = {
            "user": {"name": "John", "profile": {"theme": "dark"}},
            "metadata": {"source": "api"},
        }

        parser_config = {
            "steps": [],
        }

        result = manager.configured_parser(original_event, parser_config, flatten=True)

        # Original event should remain unchanged
        assert isinstance(original_event["user"], dict)
        assert original_event["user"]["name"] == "John"
        assert "user.name" not in original_event

        # Result should be flattened
        assert "user.name" in result
        assert result["user.name"] == "John"


class TestDuplicateSteps:
    """
    Regression tests for duplicate function names in a single pipeline.

    Before the steps-list-of-dicts change, args were stored in a flat dict keyed
    by function name, so the second rename silently overwrote the first one's args
    and neither rename executed with the correct arguments.
    """

    def test_two_renames_via_configured_parser(self):
        """Both rename steps execute with their own args, not each other's."""
        manager = ParserManager()
        event = {"first": "a", "second": "b", "other": "preserved"}

        parser_config = {
            "steps": [
                parser_step("rename", from_field="first", to_field="renamed_first"),
                parser_step("rename", from_field="second", to_field="renamed_second"),
            ],
        }

        result = manager.configured_parser(event, parser_config)

        assert "first" not in result
        assert "second" not in result
        assert result["renamed_first"] == "a"
        assert result["renamed_second"] == "b"
        assert result["other"] == "preserved"

    def test_two_renames_via_query_parser(self):
        """End-to-end: two renames in a query string both apply correctly."""
        manager = ParserManager()
        event = {"first": "a", "second": "b", "other": "preserved"}

        query = (
            'rename(from="first", to="renamed_first") | rename(from="second", to="renamed_second")'
        )
        parser_config = manager.query_parser(query)
        result = manager.configured_parser(event, parser_config)

        assert "first" not in result
        assert "second" not in result
        assert result["renamed_first"] == "a"
        assert result["renamed_second"] == "b"
        assert result["other"] == "preserved"

    def test_two_renames_second_depends_on_first(self):
        """Second rename can target a field produced by the first rename."""
        manager = ParserManager()
        event = {"original": "value"}

        query = (
            'rename(from="original", to="intermediate") | rename(from="intermediate", to="final")'
        )
        parser_config = manager.query_parser(query)
        result = manager.configured_parser(event, parser_config)

        assert "original" not in result
        assert "intermediate" not in result
        assert result["final"] == "value"

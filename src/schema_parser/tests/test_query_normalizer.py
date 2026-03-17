from schema_parser.core.utils import (
    _parse_boolean,
    _parse_key_value_pairs,
    _parse_quoted_string,
    extract_func_body,
    extract_params,
)
from schema_parser.query_normalizer import QueryNormalizer


class TestParseJson:
    """Tests for parse_json function normalization"""

    def test_parse_json_basic(self):
        """Test basic parse_json with field parameter"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert "in_place" not in result["args"]["parse_json"]

    def test_parse_json_with_in_place_true(self):
        """Test parse_json with in_place=True"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw", in_place=True)'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["parse_json"]["in_place"] is True

    def test_parse_json_with_in_place_lowercase_true(self):
        """Test parse_json with in_place=true (lowercase)"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw", in_place=true)'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["parse_json"]["in_place"] is True

    def test_parse_json_with_in_place_false(self):
        """Test parse_json with in_place=False"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw", in_place=False)'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["parse_json"]["in_place"] is False

    def test_parse_json_with_in_place_lowercase_false(self):
        """Test parse_json with in_place=false (lowercase)"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw", in_place=false)'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["parse_json"]["in_place"] is False

    def test_parse_json_with_whitespace(self):
        """Test parse_json with extra whitespace"""
        normalizer = QueryNormalizer()
        query = 'parse_json( field = "raw" , in_place = True )'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["parse_json"]["in_place"] is True

    def test_parse_json_with_dotted_field_name(self):
        """Test parse_json with dotted field name"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="event.raw")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "event.raw"
        assert "in_place" not in result["args"]["parse_json"]

    def test_parse_json_with_deeply_nested_field_name(self):
        """Test parse_json with deeply nested dotted field name"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="level1.level2.json_field", in_place=True)'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "level1.level2.json_field"
        assert result["args"]["parse_json"]["in_place"] is True

    def test_parse_json_reversed_param_order(self):
        """Test parse_json with in_place before field"""
        normalizer = QueryNormalizer()
        query = 'parse_json(in_place=True, field="raw")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["parse_json"]["in_place"] is True

    def test_parse_json_quoted_boolean_true(self):
        """Test parse_json with in_place="true" (quoted string coerced to bool)"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw", in_place="true")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["in_place"] is True

    def test_parse_json_quoted_boolean_false(self):
        """Test parse_json with in_place="false" (quoted string coerced to bool)"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw", in_place="false")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json"]
        assert result["args"]["parse_json"]["in_place"] is False

    def test_parse_json_invalid_quoted_boolean_rejected(self):
        """Test parse_json with in_place="something" is rejected"""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query('parse_json(field="raw", in_place="something")')
        assert result["steps"] == []

    def test_parse_json_unknown_param_rejected(self):
        """Test parse_json with unknown parameter is rejected"""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query('parse_json(field="raw", unknown="value")')
        assert result["steps"] == []

    def test_parse_json_missing_field_rejected(self):
        """Test parse_json without field parameter is rejected"""
        normalizer = QueryNormalizer()
        assert normalizer.parse_query("parse_json(in_place=True)")["steps"] == []
        assert normalizer.parse_query("parse_json()")["steps"] == []

    def test_parse_json_missing_comma_rejected(self):
        """Test parse_json with missing comma between params is rejected"""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query('parse_json(field="raw" in_place=True)')
        assert result["steps"] == []

    def test_parse_json_trailing_garbage_rejected(self):
        """Test parse_json with garbage after boolean value is rejected"""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query('parse_json(field="raw", in_place=True garbage)')
        assert result["steps"] == []


class TestRegex:
    """Tests for regex function normalization"""

    def test_regex_pattern_first(self):
        """Test regex with pattern parameter first"""
        normalizer = QueryNormalizer()
        query = 'regex(pattern="^test", field="raw")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["regex"]["field"] == "raw"

    def test_regex_field_first(self):
        """Test regex with field parameter first"""
        normalizer = QueryNormalizer()
        query = 'regex(field="raw", pattern="^test")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["regex"]["field"] == "raw"

    def test_regex_with_complex_pattern(self):
        """Test regex with complex pattern including escaped characters"""
        normalizer = QueryNormalizer()
        query = 'regex(field="log", pattern="^(?P<ip>\\S+) .* \\[(?P<time>[^\\]]+)\\]")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert "ip" in result["args"]["regex"]["pattern"]
        assert "time" in result["args"]["regex"]["pattern"]
        assert result["args"]["regex"]["field"] == "log"

    def test_regex_with_whitespace(self):
        """Test regex with extra whitespace"""
        normalizer = QueryNormalizer()
        query = 'regex( pattern = "^test" , field = "raw" )'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["regex"]["field"] == "raw"

    def test_regex_with_dotted_field_name(self):
        """Test regex with dotted field name"""
        normalizer = QueryNormalizer()
        query = 'regex(field="event.log", pattern="^(?P<ip>\\S+) .*")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "^(?P<ip>\\S+) .*"
        assert result["args"]["regex"]["field"] == "event.log"

    def test_regex_with_dotted_field_name_pattern_first(self):
        """Test regex with dotted field name when pattern comes first"""
        normalizer = QueryNormalizer()
        query = 'regex(pattern="^(?P<ip>\\S+) .*", field="event.log")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "^(?P<ip>\\S+) .*"
        assert result["args"]["regex"]["field"] == "event.log"

    def test_regex_with_deeply_nested_field_name(self):
        """Test regex with deeply nested dotted field name"""
        normalizer = QueryNormalizer()
        query = 'regex(field="level1.level2.log", pattern="^test")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["regex"]["field"] == "level1.level2.log"

    def test_regex_with_pipe_in_pattern(self):
        """Test regex with pipe (alternation) in pattern"""
        normalizer = QueryNormalizer()
        query = 'regex(field="raw", pattern="(?P<proto>TCP|UDP)")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "(?P<proto>TCP|UDP)"
        assert result["args"]["regex"]["field"] == "raw"

    def test_regex_with_pipe_in_pattern_pattern_first(self):
        """Test regex with pipe in pattern when pattern comes first"""
        normalizer = QueryNormalizer()
        query = 'regex(pattern="(?P<level>INFO|WARN|ERROR)", field="log")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "(?P<level>INFO|WARN|ERROR)"
        assert result["args"]["regex"]["field"] == "log"

    def test_regex_with_multiple_pipes_in_pattern(self):
        """Test regex with multiple pipe alternations in pattern"""
        normalizer = QueryNormalizer()
        query = 'regex(field="msg", pattern="(?P<status>ok|warn|error|fatal)")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "(?P<status>ok|warn|error|fatal)"
        assert result["args"]["regex"]["field"] == "msg"

    def test_regex_with_in_place_true(self):
        """Test regex with in_place=True"""
        normalizer = QueryNormalizer()
        query = 'regex(field="raw", pattern="^test", in_place=True)'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["field"] == "raw"
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["regex"]["in_place"] is True

    def test_regex_with_in_place_false(self):
        """Test regex with in_place=False"""
        normalizer = QueryNormalizer()
        query = 'regex(pattern="^test", field="raw", in_place=False)'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["regex"]["field"] == "raw"
        assert result["args"]["regex"]["in_place"] is False

    def test_regex_with_in_place_whitespace(self):
        """Test regex with in_place and extra whitespace"""
        normalizer = QueryNormalizer()
        query = 'regex( field = "raw" , pattern = "^test" , in_place = True )'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["field"] == "raw"
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["regex"]["in_place"] is True

    def test_regex_with_in_place_quoted_true(self):
        """Test regex with in_place="true" (quoted string)"""
        normalizer = QueryNormalizer()
        query = 'regex(field="raw", pattern="^test", in_place="true")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["in_place"] is True

    def test_regex_with_in_place_quoted_false(self):
        """Test regex with in_place="false" (quoted string)"""
        normalizer = QueryNormalizer()
        query = 'regex(field="raw", pattern="^test", in_place="false")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert result["args"]["regex"]["in_place"] is False

    def test_regex_with_in_place_invalid_string(self):
        """Test regex with in_place="something" (invalid) is rejected"""
        normalizer = QueryNormalizer()
        query = 'regex(field="raw", pattern="^test", in_place="something")'
        result = normalizer.parse_query(query)

        assert result["steps"] == []

    def test_regex_without_in_place_omitted(self):
        """Test regex without in_place does not add in_place to args"""
        normalizer = QueryNormalizer()
        query = 'regex(field="raw", pattern="^test")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["regex"]
        assert "in_place" not in result["args"]["regex"]

    def test_regex_missing_required_params_rejected(self):
        """Test regex with missing pattern or field is not normalized"""
        normalizer = QueryNormalizer()
        assert normalizer.parse_query('regex(field="raw")')["steps"] == []
        assert normalizer.parse_query('regex(pattern="^test")')["steps"] == []
        assert normalizer.parse_query("regex()")["steps"] == []

    def test_regex_missing_comma_between_params_rejected(self):
        """Test regex with missing comma between params is rejected."""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query('regex(field="raw" pattern="^test")')
        assert result["steps"] == []

    def test_regex_with_boolean_trailing_garbage_rejected(self):
        """Test regex with garbage after boolean value is rejected."""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query(
            'regex(field="raw", pattern="^test", in_place=True garbage)'
        )
        assert result["steps"] == []

    def test_regex_unknown_param_rejected(self):
        """Test regex with unknown param is rejected."""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query('regex(field="raw", pattern="^test", unknown="value")')
        assert result["steps"] == []

    def test_regex_pipe_in_pattern_with_pipeline(self):
        """Test regex with pipe in pattern combined with pipeline pipe separators"""
        normalizer = QueryNormalizer()
        query = (
            'parse_json(field="raw")'
            ' | regex(field="raw", pattern="(?P<proto>TCP|UDP)")'
            ' | drop(fields="temp")'
        )
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json", "regex", "drop"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["regex"]["pattern"] == "(?P<proto>TCP|UDP)"
        assert result["args"]["regex"]["field"] == "raw"
        assert result["args"]["drop"]["fields"] == "temp"

    def test_regex_complex_pattern_with_pipes_in_multiline_query(self):
        """Test regex with pipes in pattern inside a multiline query"""
        normalizer = QueryNormalizer()
        query = """
        parse_json(field="raw")
        | regex(field="raw", pattern="^(?P<level>DEBUG|INFO|WARN|ERROR) (?P<msg>.*)")
        | rename(from="msg", to="message")
        """
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json", "regex", "rename"]
        assert result["args"]["regex"]["pattern"] == "^(?P<level>DEBUG|INFO|WARN|ERROR) (?P<msg>.*)"
        assert result["args"]["regex"]["field"] == "raw"


class TestRename:
    """Tests for rename function normalization"""

    def test_rename_basic(self):
        """Test basic rename function"""
        normalizer = QueryNormalizer()
        query = 'rename(from="old_field", to="new_field")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["rename"]
        assert result["args"]["rename"]["from_field"] == "old_field"
        assert result["args"]["rename"]["to_field"] == "new_field"

    def test_rename_with_dotted_fields(self):
        """Test rename with dotted field names"""
        normalizer = QueryNormalizer()
        query = 'rename(from="event.user", to="user.name")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["rename"]
        assert result["args"]["rename"]["from_field"] == "event.user"
        assert result["args"]["rename"]["to_field"] == "user.name"

    def test_rename_with_whitespace(self):
        """Test rename with extra whitespace"""
        normalizer = QueryNormalizer()
        query = 'rename( from = "old" , to = "new" )'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["rename"]
        assert result["args"]["rename"]["from_field"] == "old"
        assert result["args"]["rename"]["to_field"] == "new"


class TestDrop:
    """Tests for drop function normalization"""

    def test_drop_basic(self):
        """Test basic drop function"""
        normalizer = QueryNormalizer()
        query = 'drop(fields="field_name")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["drop"]
        assert result["args"]["drop"]["fields"] == "field_name"

    def test_drop_with_dotted_field(self):
        """Test drop with dotted field name"""
        normalizer = QueryNormalizer()
        query = 'drop(fields="event.count")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["drop"]
        assert result["args"]["drop"]["fields"] == "event.count"

    def test_drop_with_whitespace(self):
        """Test drop with extra whitespace"""
        normalizer = QueryNormalizer()
        query = 'drop( fields = "field_name" )'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["drop"]
        assert result["args"]["drop"]["fields"] == "field_name"


class TestSet:
    """Tests for set function normalization"""

    def test_set_basic(self):
        """Test basic set function"""
        normalizer = QueryNormalizer()
        query = 'set(field="event.type", value="http_access")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["set"]
        assert result["args"]["set"]["field"] == "event.type"
        assert result["args"]["set"]["value"] == "http_access"

    def test_set_with_special_characters_in_value(self):
        """Test set with special characters in value"""
        normalizer = QueryNormalizer()
        query = 'set(field="path", value="/usr/bin/test")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["set"]
        assert result["args"]["set"]["field"] == "path"
        assert result["args"]["set"]["value"] == "/usr/bin/test"

    def test_set_with_spaces_in_value(self):
        """Test set with spaces in value"""
        normalizer = QueryNormalizer()
        query = 'set(field="message", value="Hello World")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["set"]
        assert result["args"]["set"]["field"] == "message"
        assert result["args"]["set"]["value"] == "Hello World"

    def test_set_with_whitespace(self):
        """Test set with extra whitespace"""
        normalizer = QueryNormalizer()
        query = 'set( field = "type" , value = "test" )'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["set"]
        assert result["args"]["set"]["field"] == "type"
        assert result["args"]["set"]["value"] == "test"


class TestExtract:
    """Tests for extract function normalization"""

    def test_extract_basic(self):
        """Test basic extract function"""
        normalizer = QueryNormalizer()
        query = 'extract(field="user")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["extract"]
        assert result["args"]["extract"]["field"] == "user"

    def test_extract_with_whitespace(self):
        """Test extract with extra whitespace"""
        normalizer = QueryNormalizer()
        query = 'extract( field = "user" )'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["extract"]
        assert result["args"]["extract"]["field"] == "user"

    def test_extract_with_dots_in_field_name(self):
        """Test extract with field name containing dots (treated as simple field name)"""
        normalizer = QueryNormalizer()
        query = 'extract(field="winlog.event_data")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["extract"]
        assert result["args"]["extract"]["field"] == "winlog.event_data"


class TestParseWinEventLog:
    """Tests for parse_win_event_log function normalization"""

    def test_parse_win_event_log_basic(self):
        """Test basic parse_win_event_log function"""
        normalizer = QueryNormalizer()
        query = 'parse_win_event_log(field="log_text")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_win_event_log"]
        assert result["args"]["parse_win_event_log"]["field"] == "log_text"

    def test_parse_win_event_log_with_whitespace(self):
        """Test parse_win_event_log with extra whitespace"""
        normalizer = QueryNormalizer()
        query = 'parse_win_event_log( field = "log_text" )'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_win_event_log"]
        assert result["args"]["parse_win_event_log"]["field"] == "log_text"


class TestMultipleFunctions:
    """Tests for queries with multiple functions"""

    def test_multiple_functions_with_pipes(self):
        """Test query with multiple functions separated by pipes"""
        normalizer = QueryNormalizer()
        query = (
            'parse_json(field="raw")'
            ' | regex(field="raw", pattern="^test")'
            ' | rename(from="old", to="new")'
        )
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json", "regex", "rename"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["rename"]["from_field"] == "old"
        assert result["args"]["rename"]["to_field"] == "new"

    def test_multiple_functions_with_whitespace(self):
        """Test query with multiple functions and extra whitespace"""
        normalizer = QueryNormalizer()
        query = """
        parse_json(field="raw")
        | regex(field="raw", pattern="^test")
        | drop(fields="temp")
        """
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json", "regex", "drop"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["drop"]["fields"] == "temp"  # noqa: E501

    def test_all_functions_in_sequence(self):
        """Test all functions in a single query"""
        normalizer = QueryNormalizer()
        query = (
            'parse_json(field="raw", in_place=True)'
            ' | regex(field="raw", pattern="^test")'
            ' | rename(from="old", to="new")'
            ' | drop(fields="temp")'
            ' | set(field="type", value="test")'
            ' | extract(field="user")'
            ' | parse_win_event_log(field="log")'
        )
        result = normalizer.parse_query(query)

        assert len(result["steps"]) == 7
        assert "parse_json" in result["steps"]
        assert "regex" in result["steps"]
        assert "rename" in result["steps"]
        assert "drop" in result["steps"]
        assert "set" in result["steps"]
        assert "extract" in result["steps"]
        assert "parse_win_event_log" in result["steps"]


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_empty_query(self):
        """Test empty query"""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query("")

        assert result["steps"] == []
        assert result["args"] == {}

    def test_query_with_only_whitespace(self):
        """Test query with only whitespace"""
        normalizer = QueryNormalizer()
        result = normalizer.parse_query("   \n  \t  ")

        assert result["steps"] == []
        assert result["args"] == {}

    def test_query_with_empty_pipes(self):
        """Test query with empty pipe separators"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw") || drop(fields="temp")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json", "drop"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["drop"]["fields"] == "temp"

    def test_unknown_function(self):
        """Test query with unknown function"""
        normalizer = QueryNormalizer()
        query = 'unknown_function(field="test")'
        result = normalizer.parse_query(query)

        assert result["steps"] == []
        assert result["args"] == {}

    def test_malformed_query(self):
        """Test malformed query"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw"'
        result = normalizer.parse_query(query)

        # Should not crash, but may not parse correctly
        assert isinstance(result, dict)
        assert "steps" in result
        assert "args" in result

    def test_query_with_missing_parameters(self):
        """Test query with missing required parameters"""
        normalizer = QueryNormalizer()
        query = "parse_json()"
        result = normalizer.parse_query(query)

        # Should not parse (returns None from normalize function)
        assert result["steps"] == []
        assert result["args"] == {}


class TestRealWorldExamples:
    """Tests based on real-world usage examples"""

    def test_example_from_const(self):
        """Test example query from const.py"""
        normalizer = QueryNormalizer()
        query = """parse_json(field="payload")
| regex(field="raw", pattern="[a-zA-Z0-9.]+")
| rename(from="event.user", to="user.name")
| drop(fields="event.count")
| set(field="event.type", value="http_access")"""
        result = normalizer.parse_query(query)

        assert result["steps"] == [
            "parse_json",
            "regex",
            "rename",
            "drop",
            "set",
        ]
        assert result["args"]["parse_json"]["field"] == "payload"
        assert result["args"]["regex"]["field"] == "raw"
        assert result["args"]["regex"]["pattern"] == "[a-zA-Z0-9.]+"
        assert result["args"]["rename"]["from_field"] == "event.user"
        assert result["args"]["rename"]["to_field"] == "user.name"
        assert result["args"]["drop"]["fields"] == "event.count"
        assert result["args"]["set"]["field"] == "event.type"
        assert result["args"]["set"]["value"] == "http_access"

    def test_example_from_query_normalizer_main(self):
        """Test example query from query_normalizer.py __main__"""
        normalizer = QueryNormalizer()
        query = """
        parse_json(field="raw")
        | regex(field="raw", pattern="^(?P<client_ip>\\S+) .* \\[(?P<time>[^\\]]+)\\]")
        | rename(from="event.user", to="user.name")
        | drop(fields="event.count")
        | set(field="event.type", value="http_access")
        """
        result = normalizer.parse_query(query)

        assert result["steps"] == [
            "parse_json",
            "regex",
            "rename",
            "drop",
            "set",
        ]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert "client_ip" in result["args"]["regex"]["pattern"]
        assert "time" in result["args"]["regex"]["pattern"]
        assert result["args"]["rename"]["from_field"] == "event.user"
        assert result["args"]["rename"]["to_field"] == "user.name"
        assert result["args"]["drop"]["fields"] == "event.count"
        assert result["args"]["set"]["field"] == "event.type"
        assert result["args"]["set"]["value"] == "http_access"


class TestStripComments:
    """Tests for _strip_comments method"""

    def test_basic_comment_stripping(self):
        """Test basic comment stripping at end of line"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw") # This is a comment'
        result = normalizer._strip_comments(query)

        assert result == 'parse_json(field="raw")'

    def test_line_with_only_comment(self):
        """Test line with only a comment"""
        normalizer = QueryNormalizer()
        query = '# This is a comment\nparse_json(field="raw")'
        result = normalizer._strip_comments(query)

        assert result == 'parse_json(field="raw")'

    def test_multiple_lines_with_comments(self):
        """Test multiple lines with comments"""
        normalizer = QueryNormalizer()
        query = """parse_json(field="raw") # Comment 1
regex(field="raw", pattern="^test") # Comment 2
# Full line comment
rename(from="old", to="new")"""
        result = normalizer._strip_comments(query)

        expected = """parse_json(field="raw")
regex(field="raw", pattern="^test")
rename(from="old", to="new")"""
        assert result == expected

    def test_hash_inside_string_literal(self):
        """Test that # inside string literals is preserved"""
        normalizer = QueryNormalizer()
        query = 'set(field="path", value="/usr/bin#test")'
        result = normalizer._strip_comments(query)

        assert result == 'set(field="path", value="/usr/bin#test")'

    def test_hash_inside_string_with_comment_after(self):
        """Test # inside string literal with comment after"""
        normalizer = QueryNormalizer()
        query = 'set(field="path", value="/usr/bin#test") # This is a comment'
        result = normalizer._strip_comments(query)

        assert result == 'set(field="path", value="/usr/bin#test")'

    def test_hash_in_regex_pattern(self):
        """Test # in regex pattern string"""
        normalizer = QueryNormalizer()
        query = 'regex(field="log", pattern="test#pattern")'
        result = normalizer._strip_comments(query)

        assert result == 'regex(field="log", pattern="test#pattern")'

    def test_hash_in_regex_pattern_with_comment(self):
        """Test # in regex pattern with comment after"""
        normalizer = QueryNormalizer()
        query = 'regex(field="log", pattern="test#pattern") # Comment'
        result = normalizer._strip_comments(query)

        assert result == 'regex(field="log", pattern="test#pattern")'

    def test_multiple_strings_with_hash(self):
        """Test multiple string literals with # characters"""
        normalizer = QueryNormalizer()
        query = 'set(field="field#name", value="value#here") # Comment'
        result = normalizer._strip_comments(query)

        assert result == 'set(field="field#name", value="value#here")'

    def test_escaped_quotes_in_string(self):
        """Test escaped quotes don't break string detection"""
        normalizer = QueryNormalizer()
        query = 'set(field="path", value="test\\"quote#hash") # Comment'
        result = normalizer._strip_comments(query)

        assert result == 'set(field="path", value="test\\"quote#hash")'

    def test_comment_before_string(self):
        """Test comment before a string literal"""
        normalizer = QueryNormalizer()
        query = (
            'parse_json(field="raw") # Comment before next line\nset(field="test", value="value")'
        )
        result = normalizer._strip_comments(query)

        expected = 'parse_json(field="raw")\nset(field="test", value="value")'
        assert result == expected

    def test_empty_lines_with_comments(self):
        """Test empty lines with only comments are removed"""
        normalizer = QueryNormalizer()
        query = """parse_json(field="raw")
# Comment line
regex(field="raw", pattern="^test")
# Another comment
rename(from="old", to="new")"""
        result = normalizer._strip_comments(query)

        expected = """parse_json(field="raw")
regex(field="raw", pattern="^test")
rename(from="old", to="new")"""
        assert result == expected

    def test_comment_with_whitespace(self):
        """Test comment with whitespace"""
        normalizer = QueryNormalizer()
        query = 'parse_json(field="raw")   #   Comment with spaces'
        result = normalizer._strip_comments(query)

        assert result == 'parse_json(field="raw")'

    def test_integration_with_parse_query_hash_in_string(self):
        """Test integration: parse_query with # in string value"""
        normalizer = QueryNormalizer()
        query = 'set(field="path", value="/usr/bin#test")'
        result = normalizer.parse_query(query)

        assert result["steps"] == ["set"]
        assert result["args"]["set"]["field"] == "path"
        assert result["args"]["set"]["value"] == "/usr/bin#test"

    def test_integration_with_parse_query_comments(self):
        """Test integration: parse_query with comments"""
        normalizer = QueryNormalizer()
        query = """parse_json(field="raw") # Parse JSON first
| regex(field="raw", pattern="^test") # Extract with regex
| set(field="type", value="test")"""
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json", "regex", "set"]
        assert result["args"]["parse_json"]["field"] == "raw"
        assert result["args"]["regex"]["pattern"] == "^test"
        assert result["args"]["set"]["value"] == "test"

    def test_integration_complex_with_hash_and_comments(self):
        """Test integration: complex query with # in strings and comments"""
        normalizer = QueryNormalizer()
        query = """set(field="path", value="/usr/bin#test") # Set path with hash
| parse_json(field="raw") # Parse JSON
| set(field="url", value="http://example.com#fragment") # URL with fragment"""
        result = normalizer.parse_query(query)

        assert result["steps"] == ["set", "parse_json", "set"]
        assert result["args"]["set"]["field"] == "url"
        assert result["args"]["set"]["value"] == "http://example.com#fragment"

    def test_integration_pipe_in_regex_with_comments(self):
        """Test integration: pipe in regex pattern combined with comments"""
        normalizer = QueryNormalizer()
        query = """parse_json(field="raw") # Step 1
| regex(field="raw", pattern="(?P<proto>TCP|UDP|ICMP)") # Extract protocol
| set(field="type", value="network")"""
        result = normalizer.parse_query(query)

        assert result["steps"] == ["parse_json", "regex", "set"]
        assert result["args"]["regex"]["pattern"] == "(?P<proto>TCP|UDP|ICMP)"
        assert result["args"]["set"]["value"] == "network"


class TestExtractFuncBody:
    """Tests for extract_func_body function"""

    def test_simple_function(self):
        result = extract_func_body('regex(field="raw")', "regex")
        assert result == 'field="raw"'

    def test_with_whitespace(self):
        result = extract_func_body('regex(  field = "raw"  )', "regex")
        assert result == 'field = "raw"'

    def test_wrong_func_name(self):
        result = extract_func_body('regex(field="raw")', "drop")
        assert result is None

    def test_no_opening_paren(self):
        result = extract_func_body("regex", "regex")
        assert result is None

    def test_unclosed_paren(self):
        result = extract_func_body('regex(field="raw"', "regex")
        assert result is None

    def test_empty_body(self):
        result = extract_func_body("regex()", "regex")
        assert result is None

    def test_nested_parens_in_pattern(self):
        result = extract_func_body('regex(pattern="(?P<ip>\\S+)", field="log")', "regex")
        assert 'pattern="(?P<ip>\\S+)"' in result
        assert 'field="log"' in result

    def test_quotes_with_parens_inside(self):
        """Parentheses inside quoted strings should not affect depth."""
        result = extract_func_body('regex(pattern="(a)(b)", field="x")', "regex")
        assert result == 'pattern="(a)(b)", field="x"'

    def test_func_name_with_underscore(self):
        result = extract_func_body('parse_json(field="raw")', "parse_json")
        assert result == 'field="raw"'

    def test_trailing_content_after_closing_paren(self):
        result = extract_func_body('regex(field="raw") extra', "regex")
        assert result == 'field="raw"'


class TestParseQuotedString:
    """Tests for parse_quoted_string function"""

    def test_simple_string(self):
        value, pos = _parse_quoted_string('"hello"', 0)
        assert value == "hello"
        assert pos == 7

    def test_escaped_quote(self):
        value, pos = _parse_quoted_string(r'"say \"hi\""', 0)
        assert value == 'say "hi"'

    def test_escaped_backslash(self):
        value, pos = _parse_quoted_string(r'"path\\to"', 0)
        assert value == "path\\to"

    def test_backslash_before_regular_char(self):
        value, pos = _parse_quoted_string(r'"\\S+"', 0)
        assert value == "\\S+"

    def test_unclosed_quote(self):
        value, pos = _parse_quoted_string('"unclosed', 0)
        assert value is None

    def test_empty_string(self):
        value, pos = _parse_quoted_string('""', 0)
        assert value == ""
        assert pos == 2

    def test_starting_at_offset(self):
        value, pos = _parse_quoted_string('key="value"', 4)
        assert value == "value"
        assert pos == 11

    def test_special_characters(self):
        value, pos = _parse_quoted_string('"a.b-c_d"', 0)
        assert value == "a.b-c_d"


class TestParseBoolean:
    """Tests for parse_boolean function"""

    def test_true(self):
        value, pos = _parse_boolean("True", 0)
        assert value is True
        assert pos == 4

    def test_false(self):
        value, pos = _parse_boolean("False", 0)
        assert value is False
        assert pos == 5

    def test_true_case_insensitive(self):
        value, pos = _parse_boolean("true", 0)
        assert value is True

    def test_false_case_insensitive(self):
        value, pos = _parse_boolean("false", 0)
        assert value is False

    def test_true_mixed_case(self):
        value, pos = _parse_boolean("TRUE", 0)
        assert value is True

    def test_invalid_value(self):
        value, pos = _parse_boolean("notabool", 0)
        assert value is None
        assert pos == 0

    def test_at_offset(self):
        value, pos = _parse_boolean("xxx True", 4)
        assert value is True
        assert pos == 8

    def test_true_followed_by_comma(self):
        value, pos = _parse_boolean("True, next", 0)
        assert value is True
        assert pos == 4

    def test_empty_string(self):
        value, pos = _parse_boolean("", 0)
        assert value is None
        assert pos == 0


class TestParseKeyValuePairs:
    """Tests for parse_key_value_pairs function"""

    def test_single_string_param(self):
        result = _parse_key_value_pairs('field="raw"')
        assert result == {"field": "raw"}

    def test_two_string_params(self):
        result = _parse_key_value_pairs('field="raw", pattern="^test"')
        assert result == {"field": "raw", "pattern": "^test"}

    def test_string_and_boolean(self):
        result = _parse_key_value_pairs('field="raw", in_place=True')
        assert result == {"field": "raw", "in_place": True}

    def test_boolean_false(self):
        result = _parse_key_value_pairs('field="raw", in_place=False')
        assert result == {"field": "raw", "in_place": False}

    def test_extra_whitespace(self):
        result = _parse_key_value_pairs('  field = "raw" , pattern = "^test"  ')
        assert result == {"field": "raw", "pattern": "^test"}

    def test_empty_string_returns_empty_dict(self):
        result = _parse_key_value_pairs("")
        assert result == {}

    def test_whitespace_only_returns_empty_dict(self):
        result = _parse_key_value_pairs("   ")
        assert result == {}

    def test_invalid_no_equals(self):
        result = _parse_key_value_pairs("field")
        assert result is None

    def test_invalid_value_missing(self):
        result = _parse_key_value_pairs("field=")
        assert result is None

    def test_invalid_non_bool_unquoted(self):
        result = _parse_key_value_pairs("field=notavalue")
        assert result is None

    def test_three_params(self):
        result = _parse_key_value_pairs('pattern="^test", field="raw", in_place=True')
        assert result == {"pattern": "^test", "field": "raw", "in_place": True}

    def test_unclosed_quote_returns_none(self):
        result = _parse_key_value_pairs('field="unclosed')
        assert result is None

    def test_missing_comma_between_params_returns_none(self):
        result = _parse_key_value_pairs('field="raw" pattern="^test"')
        assert result is None

    def test_boolean_with_trailing_garbage_returns_none(self):
        result = _parse_key_value_pairs('field="raw", in_place=True garbage')
        assert result is None


class TestExtractParams:
    """Tests for extract_params function"""

    def test_basic(self):
        result = extract_params('regex(field="raw", pattern="^test")', "regex")
        assert result == {"field": "raw", "pattern": "^test"}

    def test_wrong_function_name(self):
        result = extract_params('regex(field="raw")', "drop")
        assert result is None

    def test_empty_parens(self):
        result = extract_params("regex()", "regex")
        assert result is None

    def test_with_boolean(self):
        result = extract_params('regex(field="raw", pattern="^test", in_place=True)', "regex")
        assert result == {"field": "raw", "pattern": "^test", "in_place": True}

    def test_different_function(self):
        result = extract_params('parse_json(field="raw")', "parse_json")
        assert result == {"field": "raw"}

    def test_unclosed_paren(self):
        result = extract_params('regex(field="raw"', "regex")
        assert result is None


class TestSplitByPipe:
    """Tests for _split_by_pipe static method"""

    def test_simple_split(self):
        normalizer = QueryNormalizer()
        result = normalizer._split_by_pipe("a | b | c")
        assert result == ["a ", " b ", " c"]

    def test_pipe_inside_quotes_preserved(self):
        normalizer = QueryNormalizer()
        result = normalizer._split_by_pipe('regex(pattern="a|b") | drop(fields="x")')
        assert result == ['regex(pattern="a|b") ', ' drop(fields="x")']

    def test_multiple_pipes_inside_quotes(self):
        normalizer = QueryNormalizer()
        result = normalizer._split_by_pipe('regex(pattern="a|b|c|d")')
        assert result == ['regex(pattern="a|b|c|d")']

    def test_no_pipe(self):
        normalizer = QueryNormalizer()
        result = normalizer._split_by_pipe('parse_json(field="raw")')
        assert result == ['parse_json(field="raw")']

    def test_escaped_quote_does_not_break_tracking(self):
        normalizer = QueryNormalizer()
        result = normalizer._split_by_pipe(r'set(field="x", value="a\"b|c") | drop(fields="y")')
        assert len(result) == 2
        assert "|" not in result[1] or result[1].strip().startswith("drop")

    def test_empty_string(self):
        normalizer = QueryNormalizer()
        result = normalizer._split_by_pipe("")
        assert result == [""]

    def test_only_pipes(self):
        normalizer = QueryNormalizer()
        result = normalizer._split_by_pipe("||")
        assert result == ["", "", ""]

    def test_pipe_at_boundaries_of_quotes(self):
        """Pipe immediately before/after quotes should split correctly"""
        normalizer = QueryNormalizer()
        result = normalizer._split_by_pipe('"a|b"|"c|d"')
        assert result == ['"a|b"', '"c|d"']

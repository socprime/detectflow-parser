import pytest

from schema_parser.core.exceptions import ParseKvFunctionError
from schema_parser.functions.parse_kv import ParseKvFunction, parse_kv_string
from schema_parser.manager import ParserManager

GENERIC_KV_EVENT = (
    "header|product|1.0|"
    "src=192.0.2.10|user=alice|status=200|"
    "dst=192.0.2.20|"
    "tags=web, api|"
    "note=|"
    "url=https://example.com/path?a=1&b=2|msg=hello world|"
    "bytes_in=3461|bytes_out=1375|"
    "host=app.example.com|method=GET|"
    "extra=\n"
)


def test_parse_kv_string_simple():
    result = parse_kv_string("src=192.0.2.10|dst=192.0.2.20|status=200")
    assert result == {"src": "192.0.2.10", "dst": "192.0.2.20", "status": "200"}


def test_parse_kv_string_skips_non_kv_tokens():
    result = parse_kv_string("header|product|1.0|src=192.0.2.10")
    assert result == {"src": "192.0.2.10"}
    assert "header" not in result
    assert "product" not in result


def test_parse_kv_string_empty_values():
    result = parse_kv_string("note=|extra=|status=200")
    assert result == {"note": "", "extra": "", "status": "200"}


def test_parse_kv_string_empty_values_with_tab_delimiter():
    result = parse_kv_string(
        "blockReason=\turl=https://example.com/x?a=1&b=2\tvirus_name=\tblock_res=0",
        delimiter="\t",
    )
    assert result == {
        "blockReason": "",
        "url": "https://example.com/x?a=1&b=2",
        "virus_name": "",
        "block_res": "0",
    }
    assert "a" not in result
    assert "b" not in result


def test_parse_kv_string_spaces_around_equals():
    result = parse_kv_string("src = 192.0.2.10|user = alice|status= 200")
    assert result == {"src": "192.0.2.10", "user": "alice", "status": "200"}


def test_parse_kv_string_trailing_delimiter_dropped_from_last_pair():
    result = parse_kv_string("src=192.0.2.10|user=alice|")
    assert result == {"src": "192.0.2.10", "user": "alice"}


def test_parse_kv_string_multiple_trailing_delimiters_dropped():
    result = parse_kv_string("src=192.0.2.10|user=alice|||")
    assert result == {"src": "192.0.2.10", "user": "alice"}


def test_parse_kv_string_equals_in_value():
    result = parse_kv_string("url=https://example.com/x?a=1&b=2|src=192.0.2.10")
    assert result["url"] == "https://example.com/x?a=1&b=2"
    assert result["src"] == "192.0.2.10"
    assert "a" not in result
    assert "b" not in result


def test_parse_kv_string_duplicate_keys_last_wins():
    result = parse_kv_string("src=192.0.2.10|src=192.0.2.20")
    assert result == {"src": "192.0.2.20"}


def test_parse_kv_string_custom_space_delimiter():
    result = parse_kv_string("src=192.0.2.10 dst=192.0.2.20 status=200", delimiter=" ")
    assert result == {"src": "192.0.2.10", "dst": "192.0.2.20", "status": "200"}


def test_parse_kv_string_custom_tab_delimiter():
    result = parse_kv_string("src=192.0.2.10\tdst=192.0.2.20", delimiter="\t")
    assert result == {"src": "192.0.2.10", "dst": "192.0.2.20"}


def test_parse_kv_string_spaces_around_equals_with_tab_delimiter():
    result = parse_kv_string("src = 192.0.2.10\tstatus= 200", delimiter="\t")
    assert result == {"src": "192.0.2.10", "status": "200"}


def test_parse_kv_string_no_pairs():
    assert parse_kv_string("header|product|1.0") == {}


def test_parse_kv_string_empty_delimiter_raises():
    with pytest.raises(ValueError, match="delimiter must be a non-empty string"):
        parse_kv_string("src=192.0.2.10", delimiter="")


def test_parse_kv_string_custom_value_delimiter():
    result = parse_kv_string(
        "src:192.0.2.10|dst:192.0.2.20|status:200",
        value_delimiter=":",
    )
    assert result == {"src": "192.0.2.10", "dst": "192.0.2.20", "status": "200"}


def test_parse_kv_string_spaces_around_value_delimiter():
    result = parse_kv_string("src : 192.0.2.10|user : alice", value_delimiter=":")
    assert result == {"src": "192.0.2.10", "user": "alice"}


def test_parse_kv_string_value_delimiter_inside_value():
    result = parse_kv_string(
        "url:https://example.com/x:8080|src:192.0.2.10",
        value_delimiter=":",
    )
    assert result["url"] == "https://example.com/x:8080"
    assert result["src"] == "192.0.2.10"


def test_parse_kv_string_empty_value_delimiter_raises():
    with pytest.raises(ValueError, match="value_delimiter must be a non-empty string"):
        parse_kv_string("src=192.0.2.10", value_delimiter="")


def test_parse_kv_string_custom_field_and_value_delimiters():
    result = parse_kv_string(
        "src:192.0.2.10 dst:192.0.2.20 status:200",
        delimiter=" ",
        value_delimiter=":",
    )
    assert result == {"src": "192.0.2.10", "dst": "192.0.2.20", "status": "200"}


def test_parse_kv_string_mixed_event():
    result = parse_kv_string(GENERIC_KV_EVENT)
    assert result["src"] == "192.0.2.10"
    assert result["user"] == "alice"
    assert result["status"] == "200"
    assert result["dst"] == "192.0.2.20"
    assert result["tags"] == "web, api"
    assert result["note"] == ""
    assert result["url"] == "https://example.com/path?a=1&b=2"
    assert result["msg"] == "hello world"
    assert result["bytes_in"] == "3461"
    assert result["bytes_out"] == "1375"
    assert result["host"] == "app.example.com"
    assert result["method"] == "GET"
    assert result["extra"] == ""
    assert "a" not in result
    assert "b" not in result
    assert "header" not in result
    assert "product" not in result


def test_parse_kv_function_returns_parsed_dict():
    function = ParseKvFunction()
    data = {"raw": "src=192.0.2.10|user=alice"}
    result = function.execute(data=data, field="raw")
    assert result == {"src": "192.0.2.10", "user": "alice"}


def test_parse_kv_function_in_place():
    function = ParseKvFunction()
    data = {"raw": "src=192.0.2.10|user=alice", "other": "preserved"}
    result = function.execute(data=data, field="raw", in_place=True)

    assert result is data
    assert result["raw"] == {"src": "192.0.2.10", "user": "alice"}
    assert result["other"] == "preserved"


def test_parse_kv_function_nested_path():
    function = ParseKvFunction()
    data = {"event": {"original": "src=192.0.2.10|dst=192.0.2.20"}, "other": "value"}
    result = function.execute(data=data, field="event.original", in_place=True)

    assert result["event"]["original"] == {"src": "192.0.2.10", "dst": "192.0.2.20"}
    assert result["other"] == "value"


def test_parse_kv_function_missing_field():
    function = ParseKvFunction()
    data = {"other_field": "value"}
    result = function.execute(data=data, field="raw")
    assert result == data


def test_parse_kv_function_empty_string():
    function = ParseKvFunction()
    data = {"raw": "", "other": "value"}
    result = function.execute(data=data, field="raw")
    assert result == data


def test_parse_kv_function_none_field():
    function = ParseKvFunction()
    data = {"raw": None, "other": "value"}
    result = function.execute(data=data, field="raw")
    assert result == data


def test_parse_kv_function_non_string_raises():
    function = ParseKvFunction()
    data = {"raw": 123}

    with pytest.raises(ParseKvFunctionError) as exc_info:
        function.execute(data=data, field="raw")

    assert exc_info.value.field == "raw"
    assert "not a string" in str(exc_info.value)


def test_parse_kv_function_escaped_tab_delimiter():
    function = ParseKvFunction()
    data = {"raw": "src=192.0.2.10\tdst=192.0.2.20"}
    result = function.execute(data=data, field="raw", delimiter="\\t")
    assert result == {"src": "192.0.2.10", "dst": "192.0.2.20"}


def test_parse_kv_function_custom_value_delimiter():
    function = ParseKvFunction()
    data = {"raw": "src:192.0.2.10|user:alice"}
    result = function.execute(data=data, field="raw", value_delimiter=":")
    assert result == {"src": "192.0.2.10", "user": "alice"}


def test_parse_kv_via_query_parser():
    manager = ParserManager()
    event = {"raw": GENERIC_KV_EVENT}
    parser_config = manager.query_parser('parse_kv(field="raw")')
    result = manager.configured_parser(event, parser_config)

    assert result["src"] == "192.0.2.10"
    assert result["msg"] == "hello world"
    assert result["url"] == "https://example.com/path?a=1&b=2"
    assert "header" not in result


def test_parse_kv_via_query_parser_in_place():
    manager = ParserManager()
    event = {"raw": "src=192.0.2.10|user=alice", "other": "kept"}
    parser_config = manager.query_parser('parse_kv(field="raw", in_place=True)')
    result = manager.configured_parser(event, parser_config)

    assert result["raw"] == {"src": "192.0.2.10", "user": "alice"}
    assert result["other"] == "kept"


def test_parse_kv_via_query_parser_value_delimiter():
    manager = ParserManager()
    event = {"raw": "src:192.0.2.10|user:alice"}
    parser_config = manager.query_parser('parse_kv(field="raw", value_delimiter=":")')
    result = manager.configured_parser(event, parser_config)

    assert result == {"src": "192.0.2.10", "user": "alice"}

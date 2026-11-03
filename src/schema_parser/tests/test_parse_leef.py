import pytest

from schema_parser.core.exceptions import ParseLeefFunctionError
from schema_parser.functions.parse_leef import ParseLeefFunction, parse_leef_string
from schema_parser.manager import ParserManager

MCAFEE_LEEF_EVENT = (
    "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|"
    "devTime=1787906742000|src=10.1.25.86|usrName=USER1|httpStatus=200|"
    "dst=142.150.109.18|"
    "urlCategories=Personal Network Storage, Interactive Web Applications|"
    "blockReason=|"
    "url=https://docs.google.com/spreadsheets/d/abc?id=1&t=1|"
    "user_agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)|"
    "bytes_from_client=3461|bytes_to_client=1375|"
    "time_stamp=[28/Aug/2026:11:45:42 +0300]|status_code=200|"
    "virus_name=|block_res=0|application_name=Google Docs|block_list=\n"
)

SYSLOG_PREFIXED_LEEF = "<30>Aug 28 11:45:42 mcproxy mwg: " + MCAFEE_LEEF_EVENT


def test_parse_leef_string_header_and_extensions():
    result = parse_leef_string(
        "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|src=10.1.25.86|usrName=USER1",
        delimiter="|",
    )
    assert result["leef_version"] == "1.0"
    assert result["vendor"] == "McAfee"
    assert result["product"] == "Web Gateway"
    assert result["product_version"] == "12.2.23"
    assert result["event_id"] == "0"
    assert result["src"] == "10.1.25.86"
    assert result["usrName"] == "USER1"


def test_parse_leef_string_skips_syslog_prefix():
    result = parse_leef_string(SYSLOG_PREFIXED_LEEF, delimiter="|")
    assert result["leef_version"] == "1.0"
    assert result["vendor"] == "McAfee"
    assert result["src"] == "10.1.25.86"


def test_parse_leef_string_skips_rfc5424_syslog_prefix():
    result = parse_leef_string(
        "<13>1 2019-01-18T11:07:53.520Z 10.0.1.7 "
        "LEEF:1.0|Microsoft|MSExchange|2013 SP1|15345|src=10.0.1.7\tdst=10.0.0.5"
    )
    assert result["vendor"] == "Microsoft"
    assert result["product"] == "MSExchange"
    assert result["product_version"] == "2013 SP1"
    assert result["event_id"] == "15345"
    assert result["src"] == "10.0.1.7"
    assert result["dst"] == "10.0.0.5"


def test_parse_leef_string_event_id_and_version_with_spaces():
    result = parse_leef_string("LEEF:1.0|Microsoft|MSExchange|4.0 SP1|Logon Failure|cat=Failed")
    assert result["product_version"] == "4.0 SP1"
    assert result["event_id"] == "Logon Failure"
    assert result["cat"] == "Failed"


def test_parse_leef_string_header_only():
    result = parse_leef_string("LEEF:1.0|McAfee|Web Gateway|12.2.23|0")
    assert result == {
        "leef_version": "1.0",
        "vendor": "McAfee",
        "product": "Web Gateway",
        "product_version": "12.2.23",
        "event_id": "0",
    }


def test_parse_leef_string_empty_extension_values():
    result = parse_leef_string(
        "LEEF:1.0|McAfee|Web Gateway|12.2.23|81|usrName=|blockReason=",
        delimiter="|",
    )
    assert result["event_id"] == "81"
    assert result["usrName"] == ""
    assert result["blockReason"] == ""


def test_parse_leef_string_equals_in_value():
    result = parse_leef_string(
        "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|url=https://example.com/x?a=1&b=2|src=10.1.25.86",
        delimiter="|",
    )
    assert result["url"] == "https://example.com/x?a=1&b=2"
    assert result["src"] == "10.1.25.86"
    assert "a" not in result
    assert "b" not in result


def test_parse_leef_string_tab_separated_extensions():
    result = parse_leef_string("LEEF:1.0|Vendor|Product|1.0|123|src=192.0.2.10\tdst=192.0.2.20")
    assert result["src"] == "192.0.2.10"
    assert result["dst"] == "192.0.2.20"


def test_parse_leef_string_leef2_caret_delimiter():
    result = parse_leef_string("LEEF:2.0|Lancope|StealthWatch|1.0|41|^|src=192.0.2.0^dst=192.0.2.1")
    assert result["leef_version"] == "2.0"
    assert result["vendor"] == "Lancope"
    assert result["product"] == "StealthWatch"
    assert result["event_id"] == "41"
    assert result["src"] == "192.0.2.0"
    assert result["dst"] == "192.0.2.1"


def test_parse_leef_string_leef2_hex_tab_delimiter():
    result = parse_leef_string("LEEF:2.0|Vendor|Product|1.0|eid|x09|src=192.0.2.10\tdst=192.0.2.20")
    assert result["src"] == "192.0.2.10"
    assert result["dst"] == "192.0.2.20"


def test_parse_leef_string_leef2_hex_delimiter_one_to_four_digits():
    event = "LEEF:2.0|Vendor|Product|1.0|eid|{delim}|src=192.0.2.10\tdst=192.0.2.20"
    for delim in ("x9", "0x9", "x09", "0x09", "X09", "0X09", "x009", "0x0009"):
        result = parse_leef_string(event.format(delim=delim))
        assert result["src"] == "192.0.2.10", delim
        assert result["dst"] == "192.0.2.20", delim


def test_parse_leef_string_leef2_hex_caret_and_pipe():
    caret = parse_leef_string("LEEF:2.0|Vendor|Product|1.0|eid|x5E|src=192.0.2.0^dst=192.0.2.1")
    assert caret["src"] == "192.0.2.0"
    assert caret["dst"] == "192.0.2.1"

    pipe = parse_leef_string("LEEF:2.0|Vendor|Product|1.0|eid|x7c|src=192.0.2.0|dst=192.0.2.1")
    assert pipe["src"] == "192.0.2.0"
    assert pipe["dst"] == "192.0.2.1"


def test_parse_leef_string_leef2_escaped_tab_delimiter_field():
    result = parse_leef_string("LEEF:2.0|Vendor|Product|1.0|eid|\\t|src=192.0.2.10\tdst=192.0.2.20")
    assert result["src"] == "192.0.2.10"
    assert result["dst"] == "192.0.2.20"


def test_parse_leef_string_leef2_without_delimiter_field_uses_tab():
    result = parse_leef_string(
        "LEEF:2.0|Microsoft|MSExchange|2016|15345|src=10.50.1.1\tdst=2.10.20.20"
    )
    assert result["leef_version"] == "2.0"
    assert result["src"] == "10.50.1.1"
    assert result["dst"] == "2.10.20.20"


def test_parse_leef_string_leef2_header_only_with_delimiter():
    result = parse_leef_string("LEEF:2.0|Lancope|StealthWatch|1.0|41|^|")
    assert result == {
        "leef_version": "2.0",
        "vendor": "Lancope",
        "product": "StealthWatch",
        "product_version": "1.0",
        "event_id": "41",
    }


def test_parse_leef_string_leef1_does_not_consume_delimiter_field():
    result = parse_leef_string("LEEF:1.0|Vendor|Product|1.0|1|^|src=192.0.2.0^dst=192.0.2.1")
    assert result["event_id"] == "1"
    assert "src" not in result
    assert "dst" not in result


def test_parse_leef_string_explicit_delimiter():
    result = parse_leef_string(
        "LEEF:1.0|Vendor|Product|1.0|1|src=192.0.2.10 dst=192.0.2.20",
        delimiter=" ",
    )
    assert result["src"] == "192.0.2.10"
    assert result["dst"] == "192.0.2.20"


def test_parse_leef_string_leef2_header_delimiter_overrides_param():
    result = parse_leef_string(
        "LEEF:2.0|Vendor|Product|1.0|1|^|src=192.0.2.0^dst=192.0.2.1",
        delimiter="|",
    )
    assert result["src"] == "192.0.2.0"
    assert result["dst"] == "192.0.2.1"


def test_parse_leef_string_pipe_extensions_need_delimiter_param():
    result = parse_leef_string("LEEF:1.0|McAfee|Web Gateway|12.2.23|0|src=10.1.25.86|usrName=USER1")
    assert result["src"] == "10.1.25.86|usrName=USER1"
    assert "usrName" not in result


def test_parse_leef_string_case_insensitive_prefix():
    result = parse_leef_string("leef:1.0|Vendor|Product|1.0|1|src=192.0.2.10")
    assert result["leef_version"] == "1.0"
    assert result["src"] == "192.0.2.10"


def test_parse_leef_string_mcafee_event():
    result = parse_leef_string(MCAFEE_LEEF_EVENT, delimiter="|")
    assert result["leef_version"] == "1.0"
    assert result["vendor"] == "McAfee"
    assert result["product"] == "Web Gateway"
    assert result["product_version"] == "12.2.23"
    assert result["event_id"] == "0"
    assert result["src"] == "10.1.25.86"
    assert result["usrName"] == "USER1"
    assert result["httpStatus"] == "200"
    assert result["url"] == "https://docs.google.com/spreadsheets/d/abc?id=1&t=1"
    assert result["blockReason"] == ""
    assert result["virus_name"] == ""
    assert result["application_name"] == "Google Docs"
    assert result["block_list"] == ""
    assert "id" not in result


def test_parse_leef_string_missing_prefix_raises():
    with pytest.raises(ValueError, match="does not contain a LEEF payload"):
        parse_leef_string("src=192.0.2.10|dst=192.0.2.20")


def test_parse_leef_string_incomplete_header_raises():
    with pytest.raises(ValueError, match="invalid LEEF header"):
        parse_leef_string("LEEF:1.0|McAfee|Web Gateway")


def test_parse_leef_string_empty_delimiter_raises():
    with pytest.raises(ValueError, match="delimiter must be a non-empty string"):
        parse_leef_string("LEEF:1.0|Vendor|Product|1.0|1|src=1", delimiter="")


def test_parse_leef_function_returns_parsed_dict():
    function = ParseLeefFunction()
    data = {"raw": "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|src=10.1.25.86"}
    result = function.execute(data=data, field="raw")
    assert result["vendor"] == "McAfee"
    assert result["src"] == "10.1.25.86"


def test_parse_leef_function_in_place():
    function = ParseLeefFunction()
    data = {
        "raw": "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|src=10.1.25.86",
        "other": "preserved",
    }
    result = function.execute(data=data, field="raw", in_place=True)

    assert result is data
    assert result["raw"]["vendor"] == "McAfee"
    assert result["raw"]["src"] == "10.1.25.86"
    assert result["other"] == "preserved"


def test_parse_leef_function_nested_path():
    function = ParseLeefFunction()
    data = {
        "event": {"original": "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|src=10.1.25.86"},
        "other": "value",
    }
    result = function.execute(data=data, field="event.original", in_place=True)

    assert result["event"]["original"]["src"] == "10.1.25.86"
    assert result["event"]["original"]["vendor"] == "McAfee"
    assert result["other"] == "value"


def test_parse_leef_function_missing_field():
    function = ParseLeefFunction()
    data = {"other_field": "value"}
    result = function.execute(data=data, field="raw")
    assert result == data


def test_parse_leef_function_empty_string():
    function = ParseLeefFunction()
    data = {"raw": "", "other": "value"}
    result = function.execute(data=data, field="raw")
    assert result == data


def test_parse_leef_function_none_field():
    function = ParseLeefFunction()
    data = {"raw": None, "other": "value"}
    result = function.execute(data=data, field="raw")
    assert result == data


def test_parse_leef_function_empty_list():
    function = ParseLeefFunction()
    data = {"raw": [], "other": "value"}
    result = function.execute(data=data, field="raw")
    assert result == data
    assert result["raw"] == []


def test_parse_leef_function_empty_dict():
    function = ParseLeefFunction()
    data = {"raw": {}, "other": "value"}
    result = function.execute(data=data, field="raw")
    assert result == data
    assert result["raw"] == {}


def test_parse_leef_function_non_string_raises():
    function = ParseLeefFunction()
    data = {"raw": 123}

    with pytest.raises(ParseLeefFunctionError) as exc_info:
        function.execute(data=data, field="raw")

    assert exc_info.value.field == "raw"
    assert "not a string" in str(exc_info.value)


def test_parse_leef_function_invalid_payload_raises():
    function = ParseLeefFunction()
    data = {"raw": "not a leef event"}

    with pytest.raises(ParseLeefFunctionError) as exc_info:
        function.execute(data=data, field="raw")

    assert exc_info.value.field == "raw"
    assert "LEEF payload" in str(exc_info.value)


def test_parse_leef_function_escaped_tab_delimiter():
    function = ParseLeefFunction()
    data = {"raw": "LEEF:1.0|Vendor|Product|1.0|1|src=192.0.2.10\tdst=192.0.2.20"}
    result = function.execute(data=data, field="raw", delimiter="\\t")
    assert result["src"] == "192.0.2.10"
    assert result["dst"] == "192.0.2.20"


def test_parse_leef_function_pipe_delimiter_multi_pair():
    function = ParseLeefFunction()
    data = {"raw": "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|src=10.1.25.86|usrName=USER1"}
    result = function.execute(data=data, field="raw", delimiter="|")
    assert result["src"] == "10.1.25.86"
    assert result["usrName"] == "USER1"


def test_parse_leef_function_empty_delimiter_raises():
    function = ParseLeefFunction()
    data = {"raw": "LEEF:1.0|Vendor|Product|1.0|1|src=1"}

    with pytest.raises(ParseLeefFunctionError) as exc_info:
        function.execute(data=data, field="raw", delimiter="")

    assert exc_info.value.field == "raw"
    assert "delimiter must be a non-empty string" in str(exc_info.value)


def test_parse_leef_via_query_parser():
    manager = ParserManager()
    event = {"raw": MCAFEE_LEEF_EVENT}
    parser_config = manager.query_parser('parse_leef(field="raw", delimiter="|")')
    result = manager.configured_parser(event, parser_config)

    assert result["vendor"] == "McAfee"
    assert result["src"] == "10.1.25.86"
    assert result["usrName"] == "USER1"
    assert result["url"] == "https://docs.google.com/spreadsheets/d/abc?id=1&t=1"


def test_parse_leef_via_query_parser_in_place():
    manager = ParserManager()
    event = {
        "raw": "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|src=10.1.25.86",
        "other": "kept",
    }
    parser_config = manager.query_parser('parse_leef(field="raw", in_place=True)')
    result = manager.configured_parser(event, parser_config)

    assert result["raw"]["src"] == "10.1.25.86"
    assert result["raw"]["vendor"] == "McAfee"
    assert result["other"] == "kept"


def test_parse_leef_via_query_parser_syslog_prefixed():
    manager = ParserManager()
    event = {"event": {"original": SYSLOG_PREFIXED_LEEF}}
    parser_config = manager.query_parser('parse_leef(field="event.original", delimiter="|")')
    result = manager.configured_parser(event, parser_config)

    assert result["product"] == "Web Gateway"
    assert result["src"] == "10.1.25.86"

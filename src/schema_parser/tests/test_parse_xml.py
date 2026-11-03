import pytest

from schema_parser.core.exceptions import ParseXmlFunctionError
from schema_parser.functions.parse_xml import ParseXmlFunction, parse_xml_string
from schema_parser.manager import ParserManager


def test_parse_xml_string_simple():
    result = parse_xml_string("<Event><EventID>4624</EventID></Event>")
    assert result == {"Event": {"EventID": "4624"}}


def test_parse_xml_string_nested():
    xml = "<Event><System><EventID>4624</EventID><Computer>HOST</Computer></System></Event>"
    result = parse_xml_string(xml)
    assert result == {"Event": {"System": {"EventID": "4624", "Computer": "HOST"}}}


def test_parse_xml_string_attributes():
    result = parse_xml_string('<Data Name="SubjectUserName">alice</Data>')
    assert result == {"Data": {"@Name": "SubjectUserName", "#text": "alice"}}


def test_parse_xml_string_repeated_tags():
    xml = "<EventData><Data>a</Data><Data>b</Data><Data>c</Data></EventData>"
    result = parse_xml_string(xml)
    assert result == {"EventData": {"Data": ["a", "b", "c"]}}


def test_parse_xml_string_empty_element():
    result = parse_xml_string("<root><empty/></root>")
    assert result == {"root": {"empty": ""}}


def test_parse_xml_string_attributes_only():
    result = parse_xml_string('<root id="1" type="info"/>')
    assert result == {"root": {"@id": "1", "@type": "info"}}


def test_parse_xml_string_strips_namespaces():
    xml = (
        '<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">'
        "<System><EventID>4624</EventID></System>"
        "</Event>"
    )
    result = parse_xml_string(xml)
    assert result == {"Event": {"System": {"EventID": "4624"}}}
    assert "xmlns" not in str(result)


def test_parse_xml_string_prefixed_namespace():
    xml = '<ns:root xmlns:ns="http://example.com"><ns:child>value</ns:child></ns:root>'
    result = parse_xml_string(xml)
    assert result == {"root": {"child": "value"}}


def test_parse_xml_string_predefined_entities():
    result = parse_xml_string("<root>a &lt; b &amp; c &gt; d</root>")
    assert result == {"root": "a < b & c > d"}


def test_parse_xml_string_cdata():
    result = parse_xml_string("<root><![CDATA[1 < 2 & 3]]></root>")
    assert result == {"root": "1 < 2 & 3"}


def test_parse_xml_string_unicode():
    result = parse_xml_string("<root><message>Hello 世界</message></root>")
    assert result == {"root": {"message": "Hello 世界"}}


def test_parse_xml_string_strips_bom():
    result = parse_xml_string("\ufeff<root><id>1</id></root>")
    assert result == {"root": {"id": "1"}}


def test_parse_xml_string_ignores_comments():
    result = parse_xml_string("<root><!-- ignore --><id>1</id></root>")
    assert result == {"root": {"id": "1"}}


def test_parse_xml_string_rejects_xxe():
    xml = """<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>
"""
    with pytest.raises(ValueError, match="DTD"):
        parse_xml_string(xml)


def test_parse_xml_string_rejects_billion_laughs():
    xml = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
]>
<root>&lol2;</root>
"""
    with pytest.raises(ValueError, match="DTD"):
        parse_xml_string(xml)


def test_parse_xml_string_rejects_external_dtd():
    xml = """<?xml version="1.0"?>
<!DOCTYPE root SYSTEM "http://example.invalid/evil.dtd">
<root>ok</root>
"""
    with pytest.raises(ValueError, match="DTD"):
        parse_xml_string(xml)


def test_parse_xml_string_invalid_xml():
    with pytest.raises(Exception):
        parse_xml_string("<root><unclosed>")


def test_parse_xml_simple_object():
    function = ParseXmlFunction()
    data = {"xml_field": "<user><name>John</name><age>30</age></user>"}
    result = function.execute(data=data, field="xml_field")
    assert result == {"user": {"name": "John", "age": "30"}}


def test_parse_xml_invalid_xml():
    function = ParseXmlFunction()
    data = {"xml_field": "<root><unclosed>"}

    with pytest.raises(ParseXmlFunctionError) as exc_info:
        function.execute(data=data, field="xml_field")

    assert exc_info.value.field == "xml_field"
    assert exc_info.value.field_value == "<root><unclosed>"
    assert "Failed to parse XML from field `xml_field`" in str(exc_info.value)


def test_parse_xml_malformed_xml():
    function = ParseXmlFunction()
    data = {"xml_field": "not valid xml"}

    with pytest.raises(ParseXmlFunctionError) as exc_info:
        function.execute(data=data, field="xml_field")

    assert exc_info.value.field == "xml_field"
    assert "Failed to parse XML from field `xml_field`" in str(exc_info.value)


def test_parse_xml_missing_field():
    function = ParseXmlFunction()
    data = {"other_field": "value"}
    result = function.execute(data=data, field="xml_field")
    assert result == data


def test_parse_xml_empty_string():
    function = ParseXmlFunction()
    data = {"xml_field": "", "other_field": "value"}
    result = function.execute(data=data, field="xml_field")
    assert result == data


def test_parse_xml_field_is_none():
    function = ParseXmlFunction()
    data = {"xml_field": None, "other_field": "value"}
    result = function.execute(data=data, field="xml_field", in_place=True)
    assert result == data
    assert result["xml_field"] is None


def test_parse_xml_field_is_empty_list():
    function = ParseXmlFunction()
    data = {"xml_field": [], "other_field": "value"}
    result = function.execute(data=data, field="xml_field", in_place=True)
    assert result == data


def test_parse_xml_field_is_empty_dict():
    function = ParseXmlFunction()
    data = {"xml_field": {}, "other_field": "value"}
    result = function.execute(data=data, field="xml_field", in_place=True)
    assert result == data


def test_parse_xml_field_is_not_string():
    function = ParseXmlFunction()
    data = {"xml_field": 0, "other_field": "value"}

    with pytest.raises(ParseXmlFunctionError) as exc_info:
        function.execute(data=data, field="xml_field", in_place=True)

    assert exc_info.value.field == "xml_field"
    assert "not a string" in str(exc_info.value)


def test_parse_xml_whitespace_only():
    function = ParseXmlFunction()
    data = {"xml_field": "   "}

    with pytest.raises(ParseXmlFunctionError) as exc_info:
        function.execute(data=data, field="xml_field")

    assert exc_info.value.field == "xml_field"
    assert "Failed to parse XML from field `xml_field`" in str(exc_info.value)


def test_parse_xml_dtd_raises_function_error():
    function = ParseXmlFunction()
    data = {"xml_field": '<!DOCTYPE root [<!ENTITY x "x">]><root>&x;</root>'}

    with pytest.raises(ParseXmlFunctionError) as exc_info:
        function.execute(data=data, field="xml_field")

    assert "DTD" in str(exc_info.value)


def test_parse_xml_in_place():
    function = ParseXmlFunction()
    data = {"xml_field": "<user><name>John</name></user>", "other_field": "preserved"}
    result = function.execute(data=data, field="xml_field", in_place=True)

    assert result is data
    assert result["xml_field"] == {"user": {"name": "John"}}
    assert result["other_field"] == "preserved"


def test_parse_xml_in_place_invalid_xml():
    function = ParseXmlFunction()
    data = {"xml_field": "<root><unclosed>", "other_field": "preserved"}

    with pytest.raises(ParseXmlFunctionError):
        function.execute(data=data, field="xml_field", in_place=True)

    assert data["xml_field"] == "<root><unclosed>"
    assert data["other_field"] == "preserved"


def test_parse_xml_with_nested_path():
    function = ParseXmlFunction()
    data = {"event": {"raw": "<user><name>John</name></user>"}, "other": "value"}
    result = function.execute(data=data, field="event.raw", in_place=True)

    assert result["event"]["raw"] == {"user": {"name": "John"}}
    assert result["other"] == "value"


def test_parse_xml_nested_path_missing():
    function = ParseXmlFunction()
    data = {"user": {"name": "John"}}
    result = function.execute(data=data, field="user.missing", in_place=True)
    assert result == data


def test_parse_xml_windows_event_fragment():
    xml = """
    <Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
      <System>
        <EventID>4624</EventID>
        <Computer>HOST.example.com</Computer>
      </System>
      <EventData>
        <Data Name="SubjectUserName">alice</Data>
        <Data Name="LogonType">2</Data>
      </EventData>
    </Event>
    """
    result = parse_xml_string(xml)
    assert result["Event"]["System"]["EventID"] == "4624"
    assert result["Event"]["System"]["Computer"] == "HOST.example.com"
    assert result["Event"]["EventData"]["Data"] == [
        {"@Name": "SubjectUserName", "#text": "alice"},
        {"@Name": "LogonType", "#text": "2"},
    ]


def test_parse_xml_via_query():
    manager = ParserManager()
    event = {"raw": "<user><name>John</name><age>30</age></user>"}
    parser_config = manager.query_parser('parse_xml(field="raw", in_place=True)')
    result = manager.configured_parser(event, parser_config)
    assert result["raw"] == {"user": {"name": "John", "age": "30"}}

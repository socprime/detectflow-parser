import pytest

from schema_parser.functions.list_to_dict import ListToDictFunction, items_to_dict
from schema_parser.manager import ParserManager


def test_items_to_dict_list():
    items = [
        {"@Name": "SubjectUserSid", "#text": "NULL SID"},
        {"@Name": "SubjectUserName", "#text": "-"},
        {"@Name": "LogonType", "#text": "3"},
    ]
    assert items_to_dict(items, key="@Name", value="#text") == {
        "SubjectUserSid": "NULL SID",
        "SubjectUserName": "-",
        "LogonType": "3",
    }


def test_items_to_dict_single_dict():
    assert items_to_dict({"@Name": "User", "#text": "alice"}, key="@Name", value="#text") == {
        "User": "alice"
    }


def test_items_to_dict_skips_unnamed_and_non_dicts():
    items = [
        "plain",
        {"#text": "no-name"},
        {"@Name": "", "#text": "empty-name"},
        {"@Name": "Keep", "#text": "yes"},
    ]
    assert items_to_dict(items, key="@Name", value="#text") == {"Keep": "yes"}


def test_items_to_dict_duplicate_names_keep_last():
    items = [
        {"@Name": "User", "#text": "alice"},
        {"@Name": "User", "#text": "bob"},
    ]
    assert items_to_dict(items, key="@Name", value="#text") == {"User": "bob"}


def test_items_to_dict_missing_text_is_empty_string():
    assert items_to_dict({"@Name": "Empty"}, key="@Name", value="#text") == {"Empty": ""}


def test_items_to_dict_custom_key_value():
    items = [{"name": "src", "value": "10.0.0.1"}, {"name": "dst", "value": "10.0.0.2"}]
    assert items_to_dict(items, key="name", value="value") == {
        "src": "10.0.0.1",
        "dst": "10.0.0.2",
    }


def test_list_to_dict_replaces_field():
    function = ListToDictFunction()
    data = {
        "Data": [
            {"@Name": "SubjectUserSid", "#text": "NULL SID"},
            {"@Name": "LogonType", "#text": "3"},
        ],
        "other": "kept",
    }
    result = function.execute(data=data, field="Data", key="@Name", value="#text")
    assert result is data
    assert result == {
        "Data": {"SubjectUserSid": "NULL SID", "LogonType": "3"},
        "other": "kept",
    }


def test_list_to_dict_nested_path():
    function = ListToDictFunction()
    data = {
        "Event": {
            "EventData": {
                "Data": [
                    {"@Name": "IpAddress", "#text": "192.0.2.10"},
                    {"@Name": "IpPort", "#text": "50000"},
                ]
            }
        }
    }
    result = function.execute(data=data, field="Event.EventData.Data", key="@Name", value="#text")
    assert result["Event"]["EventData"]["Data"] == {
        "IpAddress": "192.0.2.10",
        "IpPort": "50000",
    }


def test_list_to_dict_single_object():
    function = ListToDictFunction()
    data = {"Data": {"@Name": "User", "#text": "alice"}}
    result = function.execute(data=data, field="Data", key="@Name", value="#text")
    assert result["Data"] == {"User": "alice"}


def test_list_to_dict_leaves_plain_dict_unchanged():
    function = ListToDictFunction()
    data = {"EventData": {"Image": "mmc.exe", "CommandLine": "mmc.exe eventvwr.msc"}}
    result = function.execute(data=data, field="EventData", key="@Name", value="#text")
    assert result["EventData"] == {"Image": "mmc.exe", "CommandLine": "mmc.exe eventvwr.msc"}


def test_list_to_dict_empty_list():
    function = ListToDictFunction()
    data = {"Data": [], "other": "kept"}
    result = function.execute(data=data, field="Data", key="@Name", value="#text")
    assert result["Data"] == {}
    assert result["other"] == "kept"


def test_list_to_dict_missing_field():
    function = ListToDictFunction()
    data = {"other": "kept"}
    result = function.execute(data=data, field="Data", key="@Name", value="#text")
    assert result == data


def test_list_to_dict_none_field():
    function = ListToDictFunction()
    data = {"Data": None, "other": "kept"}
    result = function.execute(data=data, field="Data", key="@Name", value="#text")
    assert result == data


def test_list_to_dict_rejects_non_list_non_dict():
    function = ListToDictFunction()
    data = {"Data": 0}
    with pytest.raises(ValueError, match="not a list or dict"):
        function.execute(data=data, field="Data", key="@Name", value="#text")


def test_list_to_dict_via_query():
    manager = ParserManager()
    event = {
        "Data": [
            {"@Name": "User", "#text": "alice"},
            {"@Name": "LogonType", "#text": "3"},
        ]
    }
    parser_config = manager.query_parser('list_to_dict(field="Data", key="@Name", value="#text")')
    result = manager.configured_parser(event, parser_config)
    assert result["Data"] == {"User": "alice", "LogonType": "3"}


def test_list_to_dict_after_parse_xml():
    manager = ParserManager()
    xml = (
        "<Event><EventData>"
        '<Data Name="SubjectUserName">alice</Data>'
        '<Data Name="LogonType">3</Data>'
        "</EventData></Event>"
    )
    event = {"raw": xml}
    parser_config = manager.query_parser(
        'parse_xml(field="raw")'
        ' | list_to_dict(field="Event.EventData.Data", key="@Name", value="#text")'
    )
    result = manager.configured_parser(event, parser_config)
    assert result["Event"]["EventData"]["Data"] == {
        "SubjectUserName": "alice",
        "LogonType": "3",
    }


def test_list_to_dict_custom_key_value_via_query():
    manager = ParserManager()
    event = {"attrs": [{"name": "src", "value": "10.0.0.1"}]}
    parser_config = manager.query_parser('list_to_dict(field="attrs", key="name", value="value")')
    result = manager.configured_parser(event, parser_config)
    assert result["attrs"] == {"src": "10.0.0.1"}

# DetectFlow Parser

A DSL pipeline for parsing and transforming events using a flexible query-based syntax.

## Overview

DetectFlow Parser provides a domain-specific language (DSL) for parsing and transforming event data. It supports query-based parsers and configured parsers.


## Quick Start

```python
from schema_parser.manager import ParserManager

manager = ParserManager()

# Parse an event using a query string
event = {"raw": '{"name": "John", "age": 30}'}
query = 'parse_json(field="raw", in_place=True)'

parser_config = manager.query_parser(query)
result = manager.configured_parser(event, parser_config)
print(result)
# Output: {'raw': {'name': 'John', 'age': 30}}
```

## Usage

### Query-Based Parsing

The most common way to use Schema Parser is through query strings:

```python
from schema_parser.manager import ParserManager

manager = ParserManager()

event = {"raw": '{"name": "John", "age": 30}'}
query = """
parse_json(field="raw", in_place=True)
| rename(from="raw", to="user")
| set(field="event.type", value="user_data")
"""

parser_config = manager.query_parser(query)
result = manager.configured_parser(event, parser_config)
```

### Configured Parser

You can also use a pre-configured parser dictionary. This is the same normalized
shape returned by `manager.query_parser(...)`:

```python
parser_config = {
    "steps": [
        {
            "function_name": "parse_json",
            "args": {"field": "raw", "in_place": True},
        },
        {
            "function_name": "rename",
            "args": {"from_field": "raw", "to_field": "data"},
        },
    ]
}

result = manager.configured_parser(event, parser_config)
```

## Available Functions

All functions support nested field paths using dot notation (e.g., `"user.profile.name"`). If a direct key exists with the same name as a nested path (e.g., `{"a.b": "value"}`), it will be replaced with the nested structure when using `set` or `delete` operations.

### `parse_json`

Parses a JSON string from a field.

**Parameters:**
- `field` (required): Name of the field containing the JSON string. Supports nested paths (e.g., `"event.raw"`).
- `in_place` (optional, default: `False`): If `True`, replaces the field value with parsed JSON. If `False`, returns only the parsed JSON value (must be a dict).

**Examples:**
```python
# Parse JSON and return the parsed value
parse_json(field="raw")

# Parse JSON in place (replaces field with parsed value)
parse_json(field="raw", in_place=True)

# Parse nested field
parse_json(field="event.raw", in_place=True)

# Case-insensitive boolean values are supported
parse_json(field="raw", in_place=true)
```

**Behavior:**
- When `in_place=False`: Returns only the parsed JSON (must be a dict)
- When `in_place=True`: Modifies the input data dictionary and returns it
- Silently ignores if field is missing, `None`, empty string `""`, empty array `[]`, or empty dict `{}`
- Raises `ParseJsonFunctionError` if JSON parsing fails or parsed value is not a dict when `in_place=False`

### `parse_kv`

Parses delimiter-separated `key=value` pairs from a field. Tokens that are not valid KV pairs are skipped.

**Parameters:**
- `field` (required): Name of the field containing the KV string. Supports nested paths (e.g., `"event.original"`).
- `in_place` (optional, default: `False`): If `True`, replaces the field value with the parsed dictionary. If `False`, returns only the parsed KV dictionary.
- `delimiter` (optional, default: `|`): Separator between pairs. `"\t"`, `"\n"`, and `"\r"` are interpreted as tab/newline/carriage return.
- `value_delimiter` (optional, default: `=`): Separator between key and value. `"\t"`, `"\n"`, and `"\r"` are interpreted as tab/newline/carriage return.

**Examples:**
```python
# Parse pipe-separated KV and return the parsed dictionary
parse_kv(field="raw")

# Parse in place (replaces field with parsed dictionary)
parse_kv(field="raw", in_place=True)

# Custom field delimiter (tab-separated pairs)
parse_kv(field="raw", delimiter="\\t")

# Custom value delimiter (colon-separated key/value)
parse_kv(field="raw", value_delimiter=":")
```

**Behavior:**
- Splits on the field delimiter when it is followed by `key<value_delimiter>`
- Uses the first value delimiter in each pair to separate key and value, so values may contain that character. Spaces around the value delimiter are allowed (`src = 1`)
- Skips tokens that do not look like `key<value_delimiter>value`
- Empty values such as `note=` are kept as empty strings
- A trailing field delimiter after the last pair is dropped (`user=alice|` → `alice`)
- `key<value_delimiter>` inside a value (for example `a=` in a URL) is not treated as a new field
- Silently ignores if field is missing, `None`, empty string `""`, empty array `[]`, or empty dict `{}`
- Raises `ParseKvFunctionError` if the field is not a string

**Output Example:**

```python
# Input:  {"raw": "header|1.0|src=192.0.2.10|user=alice"}
# Query:  parse_kv(field="raw")
# Output: {"src": "192.0.2.10", "user": "alice"}
```

### `parse_leef`

Parses a LEEF (Log Event Extended Format) event. The header is always `|`-separated. Extension `key=value` pairs are parsed the same way as `parse_kv`.

**Parameters:**
- `field` (required): Name of the field containing the LEEF string. Supports nested paths (e.g., `"event.original"`).
- `in_place` (optional, default: `False`): If `True`, replaces the field value with the parsed dictionary. If `False`, returns only the parsed LEEF dictionary.
- `delimiter` (optional, default: tab): Separator between extension pairs. If the event is LEEF 2.0 and the header declares a delimiter (`^`, `x09`, …), that value is used instead. Pipe-separated vendors (McAfee) must pass `delimiter="|"`.

**Examples:**
```python
# IBM-style events (tab-separated extensions)
parse_leef(field="raw")

# McAfee Web Gateway and similar (pipe-separated extensions)
parse_leef(field="raw", delimiter="|")

# Nested field, in place
parse_leef(field="event.original", delimiter="|", in_place=True)
```

**Behavior:**
- Finds `LEEF:`, so a syslog prefix before the payload is ignored
- Header fields: `leef_version`, `vendor`, `product`, `product_version`, `event_id`
- Extension delimiter: LEEF 2.0 header field, then `delimiter`, then tab. It is not guessed from the payload
- Extension pairs follow `parse_kv` (empty values kept, `=` inside values allowed)
- Silently ignores if field is missing, `None`, empty string `""`, empty array `[]`, or empty dict `{}`
- Raises `ParseLeefFunctionError` if the field is not a string or is not a LEEF event

**Output Example:**

```python
# Input:  {"raw": "LEEF:1.0|McAfee|Web Gateway|12.2.23|0|src=10.1.25.86|usrName=USER1"}
# Query:  parse_leef(field="raw", delimiter="|")
# Output: {
#     "leef_version": "1.0",
#     "vendor": "McAfee",
#     "product": "Web Gateway",
#     "product_version": "12.2.23",
#     "event_id": "0",
#     "src": "10.1.25.86",
#     "usrName": "USER1",
# }
```

### `parse_xml`

Parses an XML string into a nested dictionary.

**Parameters:**
- `field` (required): Name of the field containing the XML string. Supports nested paths (e.g., `"event.raw"`).
- `in_place` (optional, default: `False`): If `True`, replaces the field value with the parsed dictionary. If `False`, returns only the parsed XML dictionary.

**Examples:**
```python
parse_xml(field="raw")
parse_xml(field="raw", in_place=True)
parse_xml(field="event.raw", in_place=True)

# Windows Event XML: turn EventData fields into top-level keys
parse_xml(field="raw") | list_to_dict(field="Event.EventData.Data", key="@Name", value="#text") | extract(field="Event.EventData.Data")
```

Windows Event XML stores event fields as repeated `<Data Name="...">` elements. `parse_xml` leaves them as a list of `@Name` / `#text` objects; `list_to_dict` converts that list to a flat map, and `extract` promotes those keys to the top level.

**Behavior:**
- Root element name is the top-level key
- Attributes become `@Name`-style keys; element text is `#text` when the element also has attributes
- Repeated tags become lists
- Namespaces are stripped
- Missing or empty field is ignored
- Raises `ParseXmlFunctionError` if the value is not a string, the XML is invalid, or it contains a DTD

**Output Example:**

```python
# Input:  {"raw": '<Event><EventData><Data Name="User">alice</Data><Data Name="LogonType">3</Data></EventData></Event>'}
# Query:  parse_xml(field="raw")
# Output: {
#     "Event": {
#         "EventData": {
#             "Data": [
#                 {"@Name": "User", "#text": "alice"},
#                 {"@Name": "LogonType", "#text": "3"},
#             ]
#         }
#     }
# }
```

### `regex`

Extracts data from a field using a regular expression pattern.

**Parameters:**
- `pattern` (required): Regular expression pattern with named groups
- `field` (required): Name of the field to apply the regex to. Supports nested paths (e.g., `"event.log"`).
- `in_place` (optional, default: `False`): If `True`, replaces the field value with the matched groupdict and returns the modified data dictionary. If `False`, returns only the matched groupdict.

**Examples:**
```python
# Pattern first, field second
regex(pattern="^(?P<ip>\\S+) .*", field="log")

# Field first, pattern second (both orders supported)
regex(field="log", pattern="^(?P<ip>\\S+) .*")

# Apply regex to nested field
regex(field="event.log", pattern="^(?P<ip>\\S+) .*")

# Regex in place (replaces field with matched groups)
regex(field="log", pattern="^(?P<ip>\\S+) .*", in_place=True)

# Case-insensitive boolean values are supported
regex(field="log", pattern="^(?P<ip>\\S+) .*", in_place=true)
```

**`in_place` examples:**

Without `in_place` (default — returns only the matched groups):
```python
# Input:  {"log": "192.168.1.1 - GET /api"}
# Query:  regex(field="log", pattern="^(?P<ip>\\S+) .*")
# Output: {"ip": "192.168.1.1"}
```

With `in_place=True` (replaces the field value with matched groups):
```python
# Input:  {"log": "192.168.1.1 - GET /api", "other": "value"}
# Query:  regex(field="log", pattern="^(?P<ip>\\S+) .*", in_place=True)
# Output: {"log": {"ip": "192.168.1.1"}, "other": "value"}
```

With `in_place=True` on a nested field:
```python
# Input:  {"event": {"raw": "192.168.1.1 - GET /api"}, "type": "access"}
# Query:  regex(field="event.raw", pattern="^(?P<ip>\\S+) .*", in_place=True)
# Output: {"event": {"raw": {"ip": "192.168.1.1"}}, "type": "access"}
```

**Behavior:**
- When `in_place=False`: Returns only the matched groupdict
- When `in_place=True`: Replaces the field value with the matched groupdict and returns the modified data dictionary
- Raises `RegexPatternMatchError` if the field is missing or the pattern doesn't match
- Raises `RegexFieldTypeError` if the field value is not a string

### `rename`

Renames a field in the data dictionary.

**Parameters:**
- `from` (required): Current field name. Supports nested paths (e.g., `"user.profile.name"`).
- `to` (required): New field name. Supports nested paths (e.g., `"user.name"`). Creates intermediate dictionaries if needed.

**Examples:**
```python
# Simple rename
rename(from="old_field", to="new_field")

# Rename from nested path
rename(from="event.user", to="user.name")

# Rename from nested to nested
rename(from="user.profile.name", to="user.name")
```

### `extract`

Extracts a nested dictionary from a field and merges it with the parent dictionary.

**Parameters:**
- `field` (required): Name of the field containing the nested dictionary to extract. Supports nested paths (e.g., `"winlog.event_data"`).

**Examples:**
```python
# Extract a nested user object
extract(field="user")

# Example transformation:
# Input:  {'user': {'user_name': 'test', 'user_id': '1'}, 'some_field': 'some_value'}
# Output: {'user_name': 'test', 'user_id': '1', 'some_field': 'some_value'}

# Extract from nested path
extract(field="winlog.event_data")

# Empty dict is also extracted (field is removed):
# Input:  {'empty': {}, 'other': 'value'}
# Output: {'other': 'value'}
```

**Behavior:**
- Extracts the nested dictionary from the specified field (supports nested paths)
- Merges all fields from the nested dictionary into the parent
- Removes the original nested field
- Silently ignores if field is missing, `None`, empty string `""`, or empty array `[]`
- Empty dict `{}` is valid and will be extracted (field removed, nothing merged)
- Raises an error only if field exists and is not a dictionary

### `list_to_dict`

Turns a list of objects into a dictionary using two fields as key and value. Always returns the full event, with that field replaced.

```python
# Before
{"Data": [{"@Name": "User", "#text": "alice"}, {"@Name": "LogonType", "#text": "3"}]}

# After list_to_dict(field="Data", key="@Name", value="#text")
{"Data": {"User": "alice", "LogonType": "3"}}
```

**Parameters:**
- `field` (required): Path to the list (or a single object). Supports nested paths.
- `key` (required): Field used as the dictionary key.
- `value` (required): Field used as the dictionary value.

**Examples:**
```python
# Typical follow-up to parse_xml (path is on the parsed result)
parse_xml(field="raw") | list_to_dict(field="Event.EventData.Data", key="@Name", value="#text")

# Same idea when XML is kept in place — path stays under `raw`
parse_xml(field="raw", in_place=True) | list_to_dict(field="raw.Event.EventData.Data", key="@Name", value="#text")

# Any list of objects, not only XML
list_to_dict(field="attrs", key="name", value="value")
```

**Behavior:**
- A single object is treated as a one-item list
- Duplicate keys keep the last value
- Items without `key`, and non-dict items, are skipped
- Missing or empty field is ignored
- Raises `ValueError` if the field exists and is not a list or dict

### `drop`

Removes one or more fields from the data dictionary.

**Parameters:**
- `fields` (required): Field name to drop (comma-separated for multiple fields). Supports nested paths (e.g., `"user.profile.name"`).

**Examples:**
```python
# Drop a simple field
drop(fields="temp_field")

# Drop a nested field
drop(fields="event.count")

# Drop multiple fields (including nested)
drop(fields="temp_field,user.profile.name")
```

### `set`

Sets a field to a specific value.

**Parameters:**
- `field` (required): Field name to set. Supports nested paths (e.g., `"user.profile.name"`). Creates intermediate dictionaries if needed.
- `value` (required): Value to set (can be any type)

**Examples:**
```python
# Set a simple field
set(field="message", value="Hello World")

# Set a nested field (creates intermediate dicts if needed)
set(field="event.type", value="http_access")
set(field="user.profile.name", value="John")

# If a direct key exists with the same name (e.g., {"a.b": "old"}),
# it will be replaced with the nested structure
```

### `parse_win_event_log`

Parses Windows Event Log text format (typically exported from Splunk or Windows Event Viewer).

**Parameters:**
- `field` (required): Name of the field containing the Windows Event Log text
- `in_place` (optional, default: `False`): If `True`, replaces the field value with the parsed dictionary and keeps the other event fields (e.g. Splunk `_time`, `host`). If `False`, returns only the parsed dictionary.
- `parse_header_time` (optional, default: `False`): If `True`, parses the first line (`MM/DD/YYYY HH:MM:SS AM/PM`) into `TimeCreated` as ISO 8601 without a timezone. This is the forwarder host's local time, so do not use it as the event timestamp (e.g. in `timestamp_fields`); use Splunk `_time` instead. An unrecognized first line is skipped without failing the parse.
- `keep` (optional): Comma-separated fields of the input event (e.g. `"_time,host"`) to copy into the result as is, so they survive without `in_place`. Missing fields are ignored.

**Input Format:**

The function expects Windows Event Log text in the following format:

```
01/01/2025 10:00:00 AM
LogName=Security
EventCode=4648
EventType=0
ComputerName=example.com
SourceName=Microsoft Windows security auditing.
Type=Information
RecordNumber=12345
Keywords=Audit Success
TaskCategory=Logon
OpCode=Info
Message=A logon was attempted using explicit credentials.

Subject:
    Security ID:        NT AUTHORITY\SYSTEM
    Account Name:        EXAMPLE$
    Account Domain:        EXAMPLE
    Logon ID:        0x3E7

Network Information:
    Network Address:    10.10.10.10
    Port:            57200
```

**How it works:**
- Parses key-value pairs in the format `Key=Value` or `Key: Value`
- Extracts the EventID from the `EventCode` field
- Handles structured sections (e.g., "Subject:", "Network Information:")
- Maps section fields to standardized field names based on event type
- Skips the first line (timestamp) unless `parse_header_time=True`
- Handles multi-line values (continuation lines)

**Returns:** Dictionary with parsed event fields. Field names are standardized based on the event type and section mapping.

**Examples:**
```python
# Basic usage
parse_win_event_log(field="log_text")

# Keep Splunk _time and host next to the parsed fields
parse_win_event_log(field="_raw", keep="_time,host")

# Keep all Splunk metadata (_time, host, ...) and lift parsed fields to the top level
parse_win_event_log(field="_raw", in_place=True) | extract(field="_raw")

# Also add the local header time as TimeCreated (ISO 8601, no timezone)
parse_win_event_log(field="_raw", parse_header_time=True)

# In a query chain
query = """
parse_win_event_log(field="raw_log")
| rename(from="EventID", to="event.id")
| set(field="source", value="windows_event")
"""
```

**Output Example:**

For the input above, the function returns:
```python
{
    "EventID": "4648",
    "LogName": "Security",
    "EventType": "0",
    "ComputerName": "example.com",
    "SourceName": "Microsoft Windows security auditing.",
    "Type": "Information",
    "RecordNumber": "12345",
    "Keywords": "Audit Success",
    "TaskCategory": "Logon",
    "OpCode": "Info",
    "Message": "A logon was attempted using explicit credentials.",
    "SubjectUserSid": "NT AUTHORITY\\SYSTEM",
    "SubjectUserName": "EXAMPLE$",
    "SubjectDomainName": "EXAMPLE",
    "SubjectLogonId": "0x3E7",
    "IpAddress": "10.10.10.10",
    "IpPort": "57200"
}
```

**Notes:**
- Field names in sections are mapped to standardized names based on event ID and section type
- Fields outside of sections are preserved as-is
- Empty logs return an empty dictionary
- The parser handles various Windows Event Log formats and event types

### `parse_wincollect_win_event_log`

Parses Windows Event Log text as forwarded by WinCollect (`AgentDevice=WindowsLog`). WinCollect flattens the multi-line Windows Event Viewer text into a single-line, tab- and double-space-delimited string; this function reshapes that string back into the layout expected by `parse_win_event_log` and reuses its parsing and field-mapping logic.

**Parameters:**
- `field` (required): Name of the field containing the WinCollect-forwarded Windows Event Log text
- `in_place` (optional, default: `False`): If `True`, replaces the field value with the parsed dictionary and keeps the other event fields (e.g. `@timestamp`). If `False`, returns only the parsed dictionary.

**Input Format:**

Typical WinCollect payload (tabs between top-level fields; section fields packed with double spaces after `Message=`):

```
<13>Jul 13 15:18:32 HOST.sub.domain.name AgentDevice=WindowsLog	AgentLogFile=Security	PluginVersion=7.3.1.43	Source=Microsoft-Windows-Security-Auditing	Computer=HOST.sub.domain.name	OriginatingComputer=10.10.10.10	User=	Domain=	EventID=4662	EventIDCode=4662	EventType=8	EventCategory=12804	RecordNumber=3703867	TimeGenerated=1783945048	TimeWritten=1783945048	Level=Log Always	Keywords=Audit Success	Task=SE_ADT_OBJECTACCESS_OTHER	Opcode=Info	Message=An operation was performed on an object.  Subject :  Security ID:  NT AUTHORITY\LOCAL SERVICE  Account Name:  LOCAL SERVICE  Account Domain:  NT AUTHORITY  Logon ID:  0x3E5  Object:  Object Server:  LSA  Object Type:  SecretObject  Object Name:  Policy\Secrets\$MACHINE.ACC  Handle ID:  0x27058dfe690  Operation:  Operation Type:  Query  Accesses:  Query secret value       Access Mask:  0x2  Properties:  -  Additional Information:  Parameter 1:  -  Parameter 2:  -
```

**How it works:**
- Reshapes the flattened WinCollect line back into the standard Windows Event Log layout
- Splits the packed `Message=` value into individual fields (including section fields such as `Subject`/`Object`)
- Ignores free-form message text so it isn't mistaken for fields
- Delegates to `parse_win_event_log` for the actual parsing and field mapping

**Returns:** Dictionary with parsed event fields. Section fields are mapped to standardized names the same way as `parse_win_event_log`.

**Examples:**
```python
# Basic usage
parse_wincollect_win_event_log(field="log_text")

# Keep event metadata (@timestamp, ...) and lift parsed fields to the top level
parse_wincollect_win_event_log(field="event.original", in_place=True) | extract(field="event.original")

# In a query chain
query = """
parse_wincollect_win_event_log(field="raw_log")
"""
```

**Output Example:**

For an object-access event like the input above, the function returns (some fields omitted):
```python
{
    "EventID": "4662",
    "AgentLogFile": "Security",
    "Computer": "HOST.sub.domain.name",
    "Message": "An operation was performed on an object.",
    "SubjectUserSid": "NT AUTHORITY\\LOCAL SERVICE",
    "SubjectUserName": "LOCAL SERVICE",
    "SubjectDomainName": "NT AUTHORITY",
    "SubjectLogonId": "0x3E5",
    "ObjectServer": "LSA",
    "ObjectType": "SecretObject",
    "ObjectName": "Policy\\Secrets\\$MACHINE.ACC",
    "HandleId": "0x27058dfe690",
    "OperationType": "Query",
    "AccessList": "Query secret value",
    "AccessMask": "0x2",
}
```

**Notes:**
- Prefer this function for QRadar-forwarded Windows logs; use `parse_win_event_log` for native Event Viewer / Splunk multi-line text
- Missing fields return an empty dictionary; non-string field values raise `ValueError`
- Trailing Microsoft explanatory sentences after section fields are dropped so they do not corrupt the last parsed value

## Query Syntax

Queries are composed of function calls separated by pipes (`|`). Functions can be written with or without whitespace around parameters.

### Basic Syntax

```
function_name(parameter="value", parameter2="value2")
```

### Multiple Functions

Chain multiple functions using pipes:

```
parse_json(field="raw")
| regex(field="raw", pattern="^test")
| rename(from="old", to="new")
| drop(fields="temp")
| set(field="type", value="test")
```

### Whitespace Support

All functions support flexible whitespace:

```python
# All of these are valid:
parse_json(field="raw")
parse_json( field = "raw" )
parse_json(field="raw", in_place=True)
parse_json( field = "raw" , in_place = True )
```

### Comments

Queries support `#` comments. Comments are stripped from the end of lines, but `#` characters inside string literals are preserved:

```python
parse_json(field="raw") # This is a comment
set(field="path", value="/usr/bin#test") # # in strings is preserved
```

### Complete Example

```python
from schema_parser.manager import ParserManager

manager = ParserManager()

event = {
    "raw": '{"user": "john", "ip": "192.168.1.1"}',
    "log": "192.168.1.1 - GET /api/users [2024-01-01 10:00:00]"
}

query = """
parse_json(field="raw", in_place=True)
| regex(field="log", pattern="^(?P<client_ip>\\S+) .* \\[(?P<time>[^\\]]+)\\]")
| rename(from="raw.user", to="user.name")
| set(field="event.type", value="api_access")
"""

parser_config = manager.query_parser(query)
result = manager.configured_parser(event, parser_config)
```

## Error Handling

The `configured_parser` method supports error handling options:

```python
# Suppress errors and return original event
result = manager.configured_parser(
    event, 
    parser_config, 
    suppress_errors=True,
    log_errors=True
)

# Raise errors (default)
result = manager.configured_parser(event, parser_config)
```

## Requirements

- Python >= 3.10
- orjson >= 3.9.0
- xmltodict >= 0.13.0

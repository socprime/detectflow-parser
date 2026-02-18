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

You can also use a pre-configured parser dictionary:

```python
parser_config = {
    "steps": ["parse_json", "rename"],
    "args": {
        "parse_json": {"field": "raw", "in_place": True},
        "rename": {"from_field": "raw", "to_field": "data"}
    }
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

### `regex`

Extracts data from a field using a regular expression pattern.

**Parameters:**
- `pattern` (required): Regular expression pattern with named groups
- `field` (required): Name of the field to apply the regex to. Supports nested paths (e.g., `"event.log"`).

**Examples:**
```python
# Pattern first, field second
regex(pattern="^(?P<ip>\\S+) .*", field="log")

# Field first, pattern second (both orders supported)
regex(field="log", pattern="^(?P<ip>\\S+) .*")

# Apply regex to nested field
regex(field="event.log", pattern="^(?P<ip>\\S+) .*")
```

**Returns:** Dictionary with named groups from the regex pattern

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
- Skips the first line (timestamp)
- Handles multi-line values (continuation lines)

**Returns:** Dictionary with parsed event fields. Field names are standardized based on the event type and section mapping.

**Examples:**
```python
# Basic usage
parse_win_event_log(field="log_text")

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

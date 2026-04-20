import re
from typing import Any


def is_empty_value(value: Any) -> bool:
    """
    Check if a value is considered "empty" for the purposes of silently ignoring it.

    Returns True for:
    - None/null
    - Empty string ""
    - Empty list []
    - Empty dict {}

    Returns False for:
    - Non-empty strings, lists, dicts
    - Numbers (including 0)
    - Booleans (including False)
    - Other types
    """
    if value is None:
        return True
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        return True
    return False


def get_value(obj: dict[str, Any], path: str) -> Any:
    """
    Get a value from a nested dictionary using a dot-separated path.

    If the path is a single key, it will return the value of the key.
    If the path is a nested path, it will return the value of the nested path.

    Args:
        obj: The dictionary to search in
        path: The dot-separated path to the value

    Returns:
        The value at the specified path, or None if the path is not found
    """
    if path in obj:
        return obj[path]
    parts = path.split(".")
    cur: Any = obj
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def set_value(obj: dict[str, Any], path: str, value: Any) -> None:
    """
    Set a value in a nested dictionary using a dot-separated path.

    Creates intermediate dictionaries if they don't exist.
    If a direct key exists with the same name as the path (e.g., "a.b" exists as a key),
    it will be replaced with the nested structure.

    Args:
        obj: The dictionary to modify
        path: The dot-separated path to set
        value: The value to set

    Example:
        set_value({"a": {}}, "a.b.c", "value")  # {"a": {"b": {"c": "value"}}}
        set_value({"a.b": "old"}, "a.b", "new")  # {"a": {"b": "new"}}
    """
    if "." not in path:
        obj[path] = value
        return

    # If path exists as a direct key, remove it first
    if path in obj:
        del obj[path]

    parts = path.split(".")
    cur: Any = obj
    for p in parts[:-1]:
        if p not in cur:
            cur[p] = {}
        elif not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def delete_value(obj: dict[str, Any], path: str) -> Any:
    """
    Delete a value from a nested dictionary using a dot-separated path.

    If a direct key exists with the same name as the path (e.g., "a.b" exists as a key),
    it will be deleted instead of trying to access the nested path.

    Args:
        obj: The dictionary to modify
        path: The dot-separated path to delete

    Returns:
        The deleted value, or None if the path was not found

    Example:
        delete_value({"a": {"b": {"c": "value"}}}, "a.b.c")  # Returns "value"
        delete_value({"a.b": "value"}, "a.b")  # Returns "value"
    """
    if "." not in path:
        return obj.pop(path, None)

    # If path exists as a direct key, delete it first
    if path in obj:
        return obj.pop(path)

    parts = path.split(".")
    cur: Any = obj
    for p in parts[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    if not isinstance(cur, dict):
        return None
    return cur.pop(parts[-1], None)


def extract_func_body(query_part: str, func_name: str) -> str | None:
    """Extract the inner content between parentheses of func_name(...)."""
    prefix = re.match(rf"{re.escape(func_name)}\s*\(\s*", query_part)
    if not prefix:
        return None
    start = prefix.end()
    depth = 1
    i = start
    inside_string = False
    escape_next = False
    while i < len(query_part):
        c = query_part[i]
        if escape_next:
            escape_next = False
        elif c == "\\" and inside_string:
            escape_next = True
        elif c == '"':
            inside_string = not inside_string
        elif not inside_string:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return query_part[start:i].strip() or None
        i += 1
    return None


def _parse_quoted_string(text: str, pos: int) -> tuple[str | None, int]:
    """Parse a double-quoted string value starting at pos (the opening quote)."""
    pos += 1  # skip opening quote
    parts: list[str] = []
    while pos < len(text):
        c = text[pos]
        if c == "\\" and pos + 1 < len(text):
            next_c = text[pos + 1]
            if next_c in ('"', "\\"):
                parts.append(next_c)
            else:
                parts.append("\\")
                parts.append(next_c)
            pos += 2
        elif c == '"':
            return "".join(parts), pos + 1
        else:
            parts.append(c)
            pos += 1
    return None, pos  # unclosed quote


def _parse_boolean(text: str, pos: int) -> tuple[bool | None, int]:
    """Parse a boolean value (True/False, case-insensitive) starting at pos."""
    rest = text[pos:]
    if re.match(r"True\b", rest, re.IGNORECASE):
        return True, pos + 4
    if re.match(r"False\b", rest, re.IGNORECASE):
        return False, pos + 5
    return None, pos


def _skip_whitespace(text: str, pos: int) -> int:
    """Advance pos past whitespace."""
    while pos < len(text) and text[pos] in " \t\n":
        pos += 1
    return pos


def _consume_param_separator(text: str, pos: int) -> tuple[int, bool]:
    """Consume the comma separator between params."""
    if text[pos] != ",":
        return pos, False
    pos = _skip_whitespace(text, pos + 1)
    if pos >= len(text):
        return pos, False
    return pos, True


def _parse_key(text: str, pos: int) -> tuple[str | None, int]:
    """Parse 'key =' at pos. Returns (key, pos_after_equals) or (None, pos)."""
    m = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*", text[pos:])
    if not m:
        return None, pos
    return m.group(1), pos + m.end()


def _parse_value(text: str, pos: int) -> tuple[Any | None, int, bool]:
    """
    Parse a value at pos — either a quoted string or a boolean.
    Returns (value, new_pos, ok).
    """
    if pos >= len(text):
        return None, pos, False
    if text[pos] == '"':
        value, pos = _parse_quoted_string(text, pos)
        return value, pos, value is not None
    value, pos = _parse_boolean(text, pos)
    if value is None:
        return None, pos, False
    return value, pos, True


def _parse_key_value_pairs(text: str) -> dict[str, Any] | None:
    """Parse comma-separated key=value pairs (e.g. 'field="raw", in_place=True')."""
    params: dict[str, Any] = {}
    pos = _skip_whitespace(text, 0)
    first = True

    while pos < len(text):
        if not first:
            pos, has_separator = _consume_param_separator(text, pos)
            if not has_separator:
                return None

        key, pos = _parse_key(text, pos)
        if key is None:
            return None

        value, pos, ok = _parse_value(text, pos)
        if not ok:
            return None

        params[key] = value
        pos = _skip_whitespace(text, pos)
        first = False

    return params


def extract_params(query_part: str, func_name: str) -> dict[str, Any] | None:
    """
    Extract all key=value parameters from a function call like func_name(...).
    Supports quoted string values and boolean True/False values.
    Returns None if the call doesn't match func_name( or params are invalid.
    """
    body = extract_func_body(query_part, func_name)
    if body is None:
        return None
    return _parse_key_value_pairs(body)

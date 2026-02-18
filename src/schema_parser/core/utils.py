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

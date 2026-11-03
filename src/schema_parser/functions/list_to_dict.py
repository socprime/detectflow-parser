from typing import Any

from schema_parser.core.utils import get_value, set_value

from .base import BaseFunction


def items_to_dict(
    items: list[Any] | dict[str, Any],
    key: str,
    value: str,
) -> dict[str, Any]:
    """Turn a list of `{key: name, value: val}` objects into `{name: val}`.

    A single object is treated as a one-item list. Items without `key`, and
    non-dict items, are skipped. Duplicate names keep the last value.
    """
    sequence: list[Any] = items if isinstance(items, list) else [items]
    out: dict[str, Any] = {}
    for item in sequence:
        if not isinstance(item, dict):
            continue
        name = item.get(key)
        if name is None or name == "":
            continue
        raw = item.get(value)
        if raw is None or isinstance(raw, (dict, list)):
            raw = ""
        out[str(name)] = raw
    return out


class ListToDictFunction(BaseFunction):
    """Replace a list of objects with a dictionary using two fields as key and value.

    Example: `[{"@Name": "User", "#text": "alice"}]` with `key="@Name"`,
    `value="#text"` becomes `{"User": "alice"}`.
    """

    def execute(
        self,
        data: dict[str, Any],
        field: str,
        key: str,
        value: str,
    ) -> dict[str, Any]:
        field_value = get_value(data, field)

        if field_value is None or field_value == "":
            return data

        if isinstance(field_value, dict):
            if key not in field_value:
                return data
            converted = items_to_dict(field_value, key=key, value=value)
        elif isinstance(field_value, list):
            converted = items_to_dict(field_value, key=key, value=value)
        else:
            raise ValueError(f"Field `{field}` is not a list or dict, cannot convert to dict")

        set_value(data, field, converted)
        return data

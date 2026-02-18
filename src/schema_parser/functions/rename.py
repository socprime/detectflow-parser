from typing import Any

from schema_parser.core.utils import delete_value, get_value, set_value

from .base import BaseFunction


class RenameFunction(BaseFunction):
    """Function for renaming a field"""

    def execute(self, data: dict[str, Any], from_field: str, to_field: str) -> dict[str, Any]:
        field_data = get_value(data, from_field)

        if field_data is None:
            raise ValueError(f"Field {from_field} not found in data")

        deleted_value = delete_value(data, from_field)
        if deleted_value is None:
            raise ValueError(f"Field {from_field} not found in data")

        set_value(data, to_field, deleted_value)
        return data

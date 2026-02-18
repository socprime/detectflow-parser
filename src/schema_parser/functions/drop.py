from typing import Any

from schema_parser.core.utils import delete_value

from .base import BaseFunction


class DropFunction(BaseFunction):
    """Function for dropping fields"""

    def execute(self, data: dict[str, Any], fields: str) -> dict[str, Any]:
        field_list = [field.strip() for field in fields.split(",") if field.strip()]
        for field in field_list:
            delete_value(data, field)
        return data

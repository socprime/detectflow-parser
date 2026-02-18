from typing import Any

from schema_parser.core.utils import set_value

from .base import BaseFunction


class SetFunction(BaseFunction):
    def execute(self, data: dict[str, Any], field: str, value: Any) -> dict[str, Any]:
        set_value(data, field, value)
        return data

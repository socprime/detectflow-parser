import re
from typing import Any

from schema_parser.core.exceptions import (
    RegexFieldTypeError,
    RegexFunctionUnexpectedError,
    RegexPatternMatchError,
)
from schema_parser.core.utils import get_value

from .base import BaseFunction


class RegexFunction(BaseFunction):
    """Function for parsing a field using regular expression"""

    def execute(self, data: dict[str, Any], pattern: str, field: str) -> dict[str, Any]:
        try:
            field_value = get_value(data, field)

            if field_value is None:
                raise RegexPatternMatchError(
                    field=field,
                    pattern=pattern,
                    field_value="<None>",
                )
            if not isinstance(field_value, str):
                raise RegexFieldTypeError(field=field, field_type=type(field_value))

            match = re.search(pattern, field_value)
            if not match:
                raise RegexPatternMatchError(
                    field=field,
                    pattern=pattern,
                    field_value=field_value,
                )
            return match.groupdict()

        except (RegexFieldTypeError, RegexPatternMatchError):
            raise
        except Exception as e:
            raise RegexFunctionUnexpectedError(
                field=field,
                pattern=pattern,
                original_error=e,
            ) from e

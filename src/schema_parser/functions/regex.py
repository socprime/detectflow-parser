import re
from typing import Any

from schema_parser.core.exceptions import (
    RegexFieldTypeError,
    RegexFunctionUnexpectedError,
    RegexPatternMatchError,
)
from schema_parser.core.utils import get_value, set_value
from schema_parser.functions.base import BaseFunction


class RegexFunction(BaseFunction):
    """Function for parsing a field using regular expression.

    When in_place=False (default), returns the matched groupdict.
    When in_place=True, writes the groupdict to the field and returns the modified data.
    """

    def execute(
        self,
        data: dict[str, Any],
        pattern: str,
        field: str,
        in_place: bool = False,
    ) -> dict[str, Any]:
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
            groupdict = match.groupdict()
            if in_place:
                set_value(data, field, groupdict)
                return data
            return groupdict

        except (RegexFieldTypeError, RegexPatternMatchError):
            raise
        except Exception as e:
            raise RegexFunctionUnexpectedError(
                field=field,
                pattern=pattern,
                original_error=e,
            ) from e

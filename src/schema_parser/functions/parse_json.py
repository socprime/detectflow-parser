from typing import Any

import orjson

from schema_parser.core.exceptions import ParseJsonFunctionError
from schema_parser.core.utils import get_value, is_empty_value, set_value

from .base import BaseFunction


class ParseJsonFunction(BaseFunction):
    """Function for parsing JSON from a field.

    Parses a JSON string from the specified field and either returns the parsed value
    or modifies the input data dictionary in place.

    Args:
        data: Input data dictionary
        field: Name of the field containing JSON string to parse
        in_place: If True, replaces the field value with parsed JSON and returns
            the modified data dictionary. If False (default), returns only the
            parsed JSON value (must be a dict).

    Returns:
        If in_place=True: Modified data dictionary with parsed JSON in the field.
        If in_place=False: Parsed JSON value (must be a dict).

    Raises:
        ParseJsonFunctionError: If JSON parsing fails, field is missing, or
            parsed value is not a dict when in_place=False.
    """

    def execute(self, data: dict[str, Any], field: str, in_place: bool = False) -> dict[str, Any]:
        field_value = get_value(data, field)

        if field_value is None:
            # Silently ignore if field is not found
            return data

        # Treat null, empty string, empty array, and empty dict as empty (ignore them)
        if is_empty_value(field_value):
            return data

        # Field value must be a string to parse as JSON
        if not isinstance(field_value, str):
            raise ParseJsonFunctionError(
                message=f"Field `{field}` is not a string, cannot parse as JSON",
                field=field,
                field_value=field_value,
            )

        try:
            parsed_value = orjson.loads(field_value)

            if in_place:
                set_value(data, field, parsed_value)
                return data
            else:
                if isinstance(parsed_value, dict):
                    return parsed_value
                type_name = type(parsed_value).__name__
                raise ValueError(
                    f"Field `{field}` contains unsupported data type: {type_name}. "
                    f"Expected dict when in_place=False. "
                    f"Use in_place=True to parse any JSON type."
                )
        except (orjson.JSONDecodeError, ValueError) as e:
            raise ParseJsonFunctionError(
                message=f"Failed to load JSON from field `{field}` - {e}",
                field=field,
                field_value=get_value(data, field),
            )

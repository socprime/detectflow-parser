import re
from functools import lru_cache
from typing import Any

from schema_parser.core.exceptions import ParseKvFunctionError
from schema_parser.core.utils import get_value, is_empty_value, set_value

from .base import BaseFunction

_KEY_PATTERN = r"[A-Za-z_][A-Za-z0-9_.-]*"
_DELIMITER_ESCAPES = {
    "\\t": "\t",
    "\\n": "\n",
    "\\r": "\r",
}


def _unescape_delimiter(delimiter: str) -> str:
    return _DELIMITER_ESCAPES.get(delimiter, delimiter)


def _spaces_after_value_delimiter(delimiter: str) -> str:
    """Whitespace to skip after the value delimiter, excluding the pair delimiter.

    A trailing `\\s*` would consume a whitespace pair delimiter (tab, space,
    newline) when the value is empty, e.g. `blockReason=\\turl=...`, so the next
    pair would never match.
    """
    if len(delimiter) == 1 and delimiter.isspace():
        return rf"[^\S{delimiter}]*"
    if delimiter.isspace():
        return ""
    return r"\s*"


@lru_cache(maxsize=16)
def _pair_start_pattern(delimiter: str, value_delimiter: str) -> re.Pattern[str]:
    """Build a regex that finds `key<value_delimiter>` after a pair delimiter or start of string."""
    delim_re = re.escape(delimiter)
    value_delim_re = re.escape(value_delimiter)
    space_after = _spaces_after_value_delimiter(delimiter)
    return re.compile(rf"(?:^|{delim_re})\s*({_KEY_PATTERN})\s*{value_delim_re}{space_after}")


def parse_kv_string(
    text: str,
    delimiter: str = "|",
    value_delimiter: str = "=",
) -> dict[str, str]:
    """Parse delimiter-separated `key<value_delimiter>value` pairs, skipping tokens that are not KV.

    Pair boundaries are the delimiter (default `|`). The key/value separator is
    `value_delimiter` (default `=`). Tokens without that separator are ignored.
    Spaces around the value delimiter are allowed. `key<value_delimiter>` inside
    a value (for example `a=` in a URL query) is not treated as a new field. A
    trailing pair delimiter after the last pair is dropped.
    """
    if not delimiter:
        raise ValueError("delimiter must be a non-empty string")
    if not value_delimiter:
        raise ValueError("value_delimiter must be a non-empty string")

    text = text.strip()
    matches = list(_pair_start_pattern(delimiter, value_delimiter).finditer(text))
    result: dict[str, str] = {}
    last_index = len(matches) - 1
    for i, match in enumerate(matches):
        value_start = match.end()
        value_end = matches[i + 1].start() if i < last_index else len(text)
        value = text[value_start:value_end]
        if i == last_index:
            while value.endswith(delimiter):
                value = value[: -len(delimiter)]
        result[match.group(1)] = value
    return result


class ParseKvFunction(BaseFunction):
    """Function for parsing delimiter-separated key-value pairs from a field.

    Parses strings such as `key=value|key=value`, skipping tokens that are not
    valid KV pairs. Spaces around the value delimiter are allowed.

    Args:
        data: Input data dictionary
        field: Name of the field containing the KV string to parse
        in_place: If True, replaces the field value with the parsed dict and
            returns the modified data dictionary. If False (default), returns
            only the parsed KV dictionary.
        delimiter: Separator between pairs. Defaults to `|`. Common escapes
            (`\\t`, `\\n`, `\\r`) are interpreted.
        value_delimiter: Separator between key and value. Defaults to `=`.
            Common escapes (`\\t`, `\\n`, `\\r`) are interpreted.

    Returns:
        If in_place=True: Modified data dictionary with parsed KV in the field.
        If in_place=False: Parsed KV dictionary.

    Raises:
        ParseKvFunctionError: If the field is not a string.
    """

    def execute(
        self,
        data: dict[str, Any],
        field: str,
        in_place: bool = False,
        delimiter: str = "|",
        value_delimiter: str = "=",
    ) -> dict[str, Any]:
        field_value = get_value(data, field)

        if field_value is None:
            return data

        if is_empty_value(field_value):
            return data

        if not isinstance(field_value, str):
            raise ParseKvFunctionError(
                message=f"Field `{field}` is not a string, cannot parse as KV",
                field=field,
                field_value=field_value,
            )

        delimiter = _unescape_delimiter(delimiter)
        value_delimiter = _unescape_delimiter(value_delimiter)
        if not delimiter:
            raise ParseKvFunctionError(
                message="delimiter must be a non-empty string",
                field=field,
                field_value=field_value,
            )
        if not value_delimiter:
            raise ParseKvFunctionError(
                message="value_delimiter must be a non-empty string",
                field=field,
                field_value=field_value,
            )

        parsed_value = parse_kv_string(
            field_value,
            delimiter=delimiter,
            value_delimiter=value_delimiter,
        )

        if in_place:
            set_value(data, field, parsed_value)
            return data
        return parsed_value

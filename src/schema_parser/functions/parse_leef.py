import re
from typing import Any

from schema_parser.core.exceptions import ParseLeefFunctionError
from schema_parser.core.utils import get_value, is_empty_value, set_value

from .base import BaseFunction
from .parse_kv import parse_kv_string

_LEEF_PREFIX = re.compile(r"LEEF:", re.IGNORECASE)
_DELIMITER_ESCAPES = {
    "\\t": "\t",
    "\\n": "\n",
    "\\r": "\r",
}
_HEX_DELIMITER = re.compile(r"^(?:0x|x)([0-9a-fA-F]{1,4})$", re.IGNORECASE)
_HEADER_FIELD_COUNT = 5
_DEFAULT_EXTENSION_DELIMITER = "\t"


def _unescape_delimiter(delimiter: str) -> str:
    return _DELIMITER_ESCAPES.get(delimiter, delimiter)


def _decode_leef2_delimiter(field: str) -> str | None:
    """Return the LEEF 2.0 extension delimiter, or None if `field` is not one."""
    candidate = field.strip()
    if not candidate:
        return None
    hex_match = _HEX_DELIMITER.fullmatch(candidate)
    if hex_match:
        return chr(int(hex_match.group(1), 16))
    if candidate in _DELIMITER_ESCAPES:
        return _DELIMITER_ESCAPES[candidate]
    if len(candidate) == 1:
        return candidate
    return None


def parse_leef_string(text: str, delimiter: str | None = None) -> dict[str, str]:
    """Parse a LEEF event into header fields plus extension key=value pairs.

    Accepts a syslog prefix before `LEEF:`. Header fields are always
    pipe-separated. Extension pairs use the LEEF 2.0 header delimiter when
    present, otherwise `delimiter` when given, otherwise tab.
    """
    if delimiter is not None and delimiter == "":
        raise ValueError("delimiter must be a non-empty string")

    text = text.strip()
    prefix = _LEEF_PREFIX.search(text)
    if prefix is None:
        raise ValueError("string does not contain a LEEF payload")

    payload = text[prefix.end() :]
    header = payload.split("|", _HEADER_FIELD_COUNT)
    if len(header) < _HEADER_FIELD_COUNT:
        raise ValueError("invalid LEEF header")

    leef_version = header[0].strip()
    vendor = header[1].strip()
    product = header[2].strip()
    product_version = header[3].strip()
    event_id = header[4].strip()
    extensions = header[5] if len(header) > _HEADER_FIELD_COUNT else ""

    leef2_delimiter = None
    if leef_version.startswith("2") and extensions:
        delim_field, sep, remainder = extensions.partition("|")
        decoded = _decode_leef2_delimiter(delim_field)
        if decoded is not None:
            leef2_delimiter = decoded
            extensions = remainder if sep else ""

    attr_delimiter = leef2_delimiter or delimiter or _DEFAULT_EXTENSION_DELIMITER

    result: dict[str, str] = {
        "leef_version": leef_version,
        "vendor": vendor,
        "product": product,
        "product_version": product_version,
        "event_id": event_id,
    }
    if extensions:
        result.update(parse_kv_string(extensions, delimiter=attr_delimiter))
    return result


class ParseLeefFunction(BaseFunction):
    """Function for parsing LEEF events from a field.

    Parses strings such as `LEEF:1.0|Vendor|Product|1.0|0|src=1.1.1.1\\tdst=2.2.2.2`.
    A syslog prefix before `LEEF:` is ignored. Header fields are returned
    alongside extension key=value pairs.

    Args:
        data: Input data dictionary
        field: Name of the field containing the LEEF string to parse
        in_place: If True, replaces the field value with the parsed dict and
            returns the modified data dictionary. If False (default), returns
            only the parsed LEEF dictionary.
        delimiter: Separator between extension pairs. A LEEF 2.0 header
            delimiter takes priority when present. Otherwise this argument is
            used, otherwise tab. Pipe-separated vendors (for example McAfee)
            must pass `delimiter="|"`. Common escapes (`\\t`, `\\n`, `\\r`)
            are interpreted.

    Returns:
        If in_place=True: Modified data dictionary with parsed LEEF in the field.
        If in_place=False: Parsed LEEF dictionary.

    Raises:
        ParseLeefFunctionError: If the field is not a string or is not LEEF.
    """

    def execute(
        self,
        data: dict[str, Any],
        field: str,
        in_place: bool = False,
        delimiter: str | None = None,
    ) -> dict[str, Any]:
        field_value = get_value(data, field)

        if field_value is None:
            return data

        if is_empty_value(field_value):
            return data

        if not isinstance(field_value, str):
            raise ParseLeefFunctionError(
                message=f"Field `{field}` is not a string, cannot parse as LEEF",
                field=field,
                field_value=field_value,
            )

        if delimiter is not None:
            delimiter = _unescape_delimiter(delimiter)
            if not delimiter:
                raise ParseLeefFunctionError(
                    message="delimiter must be a non-empty string",
                    field=field,
                    field_value=field_value,
                )

        try:
            parsed_value = parse_leef_string(field_value, delimiter=delimiter)
        except ValueError as e:
            raise ParseLeefFunctionError(
                message=f"Failed to parse LEEF from field `{field}` - {e}",
                field=field,
                field_value=field_value,
            ) from e

        if in_place:
            set_value(data, field, parsed_value)
            return data
        return parsed_value

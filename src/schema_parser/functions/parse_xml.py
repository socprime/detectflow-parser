from typing import Any
from xml.parsers.expat import ExpatError

import xmltodict

from schema_parser.core.exceptions import ParseXmlFunctionError
from schema_parser.core.utils import get_value, is_empty_value, set_value

from .base import BaseFunction

_DOCTYPE_MARK = "<!DOCTYPE"
_ENTITY_MARK = "<!ENTITY"


class _StripNamespaces(dict):
    """xmltodict namespace map that always strips the URI, keeping local names."""

    def __missing__(self, _key: str) -> None:
        return None


class _ForbiddenXmlFeatureError(ValueError):
    """Raised when XML contains DTDs or entity declarations."""


def _reject_dtds(payload: str) -> None:
    """Reject DTDs before parsing.

    xmltodict disables entity expansion by default, but a DOCTYPE with no
    entities would still be accepted. Log events do not need DTDs.
    """
    if _DOCTYPE_MARK in payload or _ENTITY_MARK in payload:
        raise _ForbiddenXmlFeatureError("XML DTDs are not allowed")


def _postprocess(_path: Any, key: str, value: Any) -> tuple[str, Any] | None:
    """Drop xmlns declarations and treat empty elements as empty strings."""
    if key == "@xmlns" or key.startswith("@xmlns:"):
        return None
    if value is None:
        return key, ""
    return key, value


def parse_xml_string(text: str) -> dict[str, Any]:
    """Parse an XML string into a dictionary.

    The root element name is the top-level key. Attributes use an `@` prefix,
    repeated child tags become lists, text-only leaves are strings, and XML
    namespaces are stripped. `xmlns` declarations are dropped.
    """
    payload = text.lstrip("\ufeff")
    _reject_dtds(payload)
    parsed = xmltodict.parse(
        payload,
        process_namespaces=True,
        namespaces=_StripNamespaces(),
        postprocessor=_postprocess,
        dict_constructor=dict,
        disable_entities=True,
    )
    if not isinstance(parsed, dict):
        raise ValueError("XML root is not an element")
    return parsed


class ParseXmlFunction(BaseFunction):
    """Function for parsing XML from a field.

    Parses an XML string from the specified field and either returns the parsed
    dictionary or modifies the input data dictionary in place.

    Args:
        data: Input data dictionary
        field: Name of the field containing XML string to parse
        in_place: If True, replaces the field value with parsed XML and returns
            the modified data dictionary. If False (default), returns only the
            parsed XML dictionary.

    Returns:
        If in_place=True: Modified data dictionary with parsed XML in the field.
        If in_place=False: Parsed XML dictionary.

    Raises:
        ParseXmlFunctionError: If XML parsing fails or the field is not a string.
    """

    def execute(self, data: dict[str, Any], field: str, in_place: bool = False) -> dict[str, Any]:
        field_value = get_value(data, field)

        if field_value is None:
            return data

        if is_empty_value(field_value):
            return data

        if not isinstance(field_value, str):
            raise ParseXmlFunctionError(
                message=f"Field `{field}` is not a string, cannot parse as XML",
                field=field,
                field_value=field_value,
            )

        try:
            parsed_value = parse_xml_string(field_value)
        except (ExpatError, ValueError) as e:
            raise ParseXmlFunctionError(
                message=f"Failed to parse XML from field `{field}` - {e}",
                field=field,
                field_value=field_value,
            ) from e

        if in_place:
            set_value(data, field, parsed_value)
            return data
        return parsed_value

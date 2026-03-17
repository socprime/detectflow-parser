import re
from typing import Any

from schema_parser.core.utils import extract_params


class QueryNormalizer:
    """
    Normalizes parser query strings into structured configuration.

    Parses query strings containing function calls (e.g., parse_json, regex, rename)
    separated by pipes and converts them into a normalized format with steps and arguments.
    """

    def __init__(self):
        self.normalize_functions = {
            "parse_json": self.json_normalize,
            "regex": self.regex_normalize,
            "rename": self.rename_normalize,
            "drop": self.drop_normalize,
            "set": self.set_normalize,
            "parse_win_event_log": self.parse_win_event_log_normalize,
            "extract": self.extract_normalize,
        }

    def json_normalize(self, query_part: str) -> dict[str, Any]:
        if not query_part.strip().startswith("parse_json"):
            return None
        params = extract_params(query_part.strip(), "parse_json")
        if params is None:
            return None
        allowed_params = {"field", "in_place"}
        if any(key not in allowed_params for key in params):
            return None
        if "field" not in params or not isinstance(params["field"], str):
            return None
        result: dict[str, Any] = {"field": params["field"]}
        if "in_place" in params:
            value = params["in_place"]
            if isinstance(value, bool):
                result["in_place"] = value
            elif isinstance(value, str) and value.lower() in ("true", "false"):
                result["in_place"] = value.lower() == "true"
            else:
                return None
        return {"parse_json": result}

    def regex_normalize(self, query_part: str) -> dict[str, Any]:
        # Extract all params from regex(...) and validate required ones (pattern, field).
        # Handles any order and optional in_place (True/False).
        if not query_part.strip().startswith("regex"):
            return None
        params = extract_params(query_part.strip(), "regex")
        if params is None:
            return None
        allowed_params = {"pattern", "field", "in_place"}
        if any(key not in allowed_params for key in params):
            return None
        if "pattern" not in params or "field" not in params:
            return None
        if not isinstance(params["pattern"], str) or not isinstance(params["field"], str):
            return None
        result: dict[str, Any] = {
            "pattern": params["pattern"],
            "field": params["field"],
        }
        if "in_place" in params:
            value = params["in_place"]
            if isinstance(value, bool):
                result["in_place"] = value
            elif isinstance(value, str) and value.lower() in ("true", "false"):
                result["in_place"] = value.lower() == "true"
            else:
                return None
        return {"regex": result}

    def rename_normalize(self, query_part: str) -> dict[str, Any]:
        # Match rename with from and to parameters
        # Note: execute method expects from_field and to_field
        # Also handles whitespace around = and after commas
        regex = (
            r"rename\s*\("
            r"\s*from\s*=\s*\"(?P<from>[a-zA-Z0-9_\.\-]*)\""
            r"\s*,\s*to\s*=\s*\"(?P<to>[a-zA-Z0-9_\.\-]*)\""
            r"\s*\)"
        )
        match = re.search(regex, query_part)
        if match:
            return {
                "rename": {
                    "from_field": match.group("from"),
                    "to_field": match.group("to"),
                }
            }
        return None

    def drop_normalize(self, query_part: str) -> dict[str, Any]:
        # Also handles whitespace around = and parentheses
        regex = r"drop\s*\(\s*fields\s*=\s*\"(?P<fields>[a-zA-Z0-9_\.\-]*)\"\s*\)"
        match = re.search(regex, query_part)
        if match:
            return {"drop": {"fields": match.group("fields")}}
        return None

    def set_normalize(self, query_part: str) -> dict[str, Any]:
        # Match set with field and value parameters
        # Note: value can be any string, not just alphanumeric
        # Also handles whitespace around = and after commas
        regex = (
            r"set\s*\("
            r"\s*field\s*=\s*\"(?P<field>[a-zA-Z0-9_\.\-]*)\""
            r"\s*,\s*value\s*=\s*\"(?P<value>.*?)\""
            r"\s*\)"
        )
        match = re.search(regex, query_part)
        if match:
            return {
                "set": {
                    "field": match.group("field"),
                    "value": match.group("value"),
                }
            }
        return None

    def parse_win_event_log_normalize(self, query_part: str) -> dict[str, Any]:
        # Match parse_win_event_log with field parameter
        # Handles: parse_win_event_log(field="log_text")
        # Also handles whitespace around = and parentheses
        regex = (
            r"parse_win_event_log\s*\("
            r"\s*field\s*=\s*\"(?P<field>[a-zA-Z0-9_\.\-]*)\""
            r"\s*\)"
        )
        match = re.search(regex, query_part)
        if match:
            return {"parse_win_event_log": {"field": match.group("field")}}
        return None

    def extract_normalize(self, query_part: str) -> dict[str, Any]:
        # Match extract with field parameter
        # Handles: extract(field="user") or extract(field="winlog.event_data")
        # Also handles whitespace around = and parentheses
        regex = (
            r"extract\s*\("
            r"\s*field\s*=\s*\"(?P<field>[a-zA-Z0-9_\.\-]*)\""
            r"\s*\)"
        )
        match = re.search(regex, query_part)
        if match:
            return {"extract": {"field": match.group("field")}}
        return None

    def normalize_query_part(self, query_part: str) -> tuple[str, dict[str, Any] | None]:
        for function_name, normalize_function in self.normalize_functions.items():
            if query_part.startswith(function_name):
                try:
                    result = normalize_function(query_part)
                    if result:
                        return (function_name, result)
                except Exception as e:
                    print(f"Error normalizing query part: {e}")
                    return function_name, None
        return None, None

    def parse_query(self, parser_query: str):
        parser_query = self._strip_comments(parser_query)
        normalized_query: dict[str, Any] = {"steps": [], "args": {}}
        for query_part in self._split_by_pipe(parser_query):
            query_part = query_part.strip()
            if not query_part:
                continue
            function_name, result = self.normalize_query_part(query_part)
            if result:
                normalized_query["steps"].append(function_name)
                normalized_query["args"].update(result)
        return normalized_query

    @staticmethod
    def _split_by_pipe(query: str) -> list[str]:
        """
        Split query by pipe characters that are outside of quoted strings.

        Pipe characters inside double-quoted strings (e.g. in regex patterns)
        are preserved as part of the string value rather than treated as
        function separators.
        """
        parts: list[str] = []
        current: list[str] = []
        inside_string = False
        escape_next = False

        for char in query:
            if escape_next:
                current.append(char)
                escape_next = False
                continue

            if char == "\\":
                current.append(char)
                escape_next = True
                continue

            if char == '"':
                inside_string = not inside_string
                current.append(char)
                continue

            if char == "|" and not inside_string:
                parts.append("".join(current))
                current = []
                continue

            current.append(char)

        parts.append("".join(current))
        return parts

    @staticmethod
    def _strip_comments(query: str) -> str:
        """
        Strip comments from query string.

        Handles # comments while preserving # characters inside string literals.
        Comments start with # and continue to the end of the line, but only
        if the # is not inside a double-quoted string.

        Args:
            query: Query string that may contain comments

        Returns:
            Query string with comments removed, preserving string literals
        """
        lines = []
        for line in query.splitlines():
            # Track if we're inside a string literal
            inside_string = False
            escape_next = False
            comment_start = -1

            for i, char in enumerate(line):
                if escape_next:
                    escape_next = False
                    continue

                if char == "\\":
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    inside_string = not inside_string
                    continue

                # Only treat # as comment if we're not inside a string
                if char == "#" and not inside_string:
                    comment_start = i
                    break

            # Remove comment if found
            if comment_start != -1:
                line = line[:comment_start].rstrip()

            # Keep line if it has non-whitespace content
            if line.strip():
                lines.append(line)

        return "\n".join(lines)

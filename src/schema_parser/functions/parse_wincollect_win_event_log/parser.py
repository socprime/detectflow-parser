import re
from typing import Any

from schema_parser.core.utils import get_value, set_value

from ..base import BaseFunction
from ..parse_win_event_log.parser import ParseWinEventLogFunction

_win_event_log_parser = ParseWinEventLogFunction()

# "EventID=" / "EventIDCode=" -> "EventCode=" (parse_win_event_log keys off "EventCode=";
# WinCollect emits "EventID=" and/or "EventIDCode="). Applied once to the whole log.
_EVENT_ID_RE = re.compile(r"^EventID(?:Code)?=(\d+)$", flags=re.MULTILINE)
# First "  Key:  " / "  Section:  " delimiter inside the Message= value. Everything before this
# is free-form message text and must be left intact (it can contain "  " that are not field
# delimiters, e.g. "Processing.   List of applicable...").
_STRUCTURED_START_RE = re.compile(r"  ([A-Za-z][^:\n]*:)  ")
# Field-name characters used when deciding whether a token is a "Key: value" packed into one
# piece (single space after the colon) vs a plain value that happens to contain ":" (e.g. a
# Windows path "C:\Windows\...").
_FIELD_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 \(\)/_-]*$")


def _looks_like_field_key(token: str) -> bool:
    """True if `token` is a section/key header or a packed "Key: value" field."""
    if token.endswith(":"):
        return True
    if ":" not in token:
        return False
    key, _, rest = token.partition(":")
    key = key.strip()
    # Drive-letter paths like "C:\Windows\..." are values, not field keys.
    if len(key) == 1 and key.isalpha() and rest.startswith("\\"):
        return False
    return bool(_FIELD_NAME_RE.fullmatch(key))


def _reshape_message_region(message: str) -> str:
    """Split the double-space-delimited Message= region into one field per line."""
    structured = _STRUCTURED_START_RE.search(message)
    if not structured:
        return message

    head, tail = message[: structured.start()], message[structured.start() :]
    parts = re.split(r" {2,}", tail.strip())
    out: list[str] = [head.rstrip(), "\n"]
    i = 0
    n = len(parts)
    while i < n:
        token = parts[i].strip()
        if not token:
            i += 1
            continue

        if token.endswith(":"):
            nxt = parts[i + 1].strip() if i + 1 < n else ""
            # Section header when the next token is itself a key / packed "Key: value".
            # Plain values (including Windows paths) never look like field keys.
            if nxt and _looks_like_field_key(nxt):
                out.append(token)
                out.append("\n")
                i += 1
            elif nxt:
                out.append("    ")
                out.append(token)
                out.append("  ")
                out.append(nxt)
                out.append("\n")
                i += 2
            else:
                out.append(token)
                out.append("\n")
                i += 1
            continue

        # Packed "Key: Value" (single space after the colon), e.g. "Restricted Admin Mode: No".
        if _looks_like_field_key(token):
            out.append("    ")
            out.append(token)
            out.append("\n")
            i += 1
            continue

        # Free-form prose / bullets. Emit behind a blank line so parse_win_event_log's
        # line-continuation logic does not glue them onto the previous field's value.
        out.append("\n")
        out.append(token)
        out.append("\n")
        i += 1

    return "".join(out)


def _transform_wincollect_win_log_to_standard_win_log(log: str) -> str:
    """Reshape a WinCollect-forwarded Windows event log line into the layout
    `ParseWinEventLogFunction` expects (one field per line, with section fields indented
    under their `Section:` header), so it can be parsed by the same logic used for native
    Windows Event Viewer text exports.
    """
    log = log.replace("\t", "\n")
    log = _EVENT_ID_RE.sub(r"EventCode=\1\nEventID=\1", log, count=1)

    # The double-space-delimited nested content only ever lives in the trailing "Message=" value;
    # the preceding "Key=Value" lines never contain the "Key:  Value" delimiter.
    message_start = log.find("\nMessage=")
    if message_start == -1:
        message_start = 0 if log.startswith("Message=") else len(log)
    head, message = log[:message_start], log[message_start:]
    return head + _reshape_message_region(message)


class ParseWincollectWinEventLogFunction(BaseFunction):
    """Function for parsing a Windows event log as forwarded by WinCollect.

    WinCollect flattens the multi-line Windows Event Viewer text into a single-line, tab- and
    double-space-delimited string. This function reshapes that string back into the standard
    Windows event log layout and then reuses `ParseWinEventLogFunction` to extract fields
    (including section fields such as `Subject`/`Object`, mapped to their sigma field names
    via `field_mapping.csv`).

    Example of the log text:

    <13>Jul 13 15:18:32 HOST.sub.domain.name AgentDevice=WindowsLog\tAgentLogFile=Security\t
    PluginVersion=7.3.1.43\tSource=Microsoft-Windows-Security-Auditing\tComputer=HOST.sub.domain.name\t
    EventID=4662\tEventIDCode=4662\t...\tMessage=An operation was performed on an object.
      Subject :  Security ID:  NT AUTHORITY\\LOCAL SERVICE  Account Name:  LOCAL SERVICE  ...
    """

    def execute(self, data: dict[str, Any], field: str, in_place: bool = False) -> dict[str, Any]:
        field_value = get_value(data, field)

        if field_value is None:
            return data if in_place else {}

        if not isinstance(field_value, str):
            raise ValueError(
                f"Field `{field}` is not a string, cannot parse as a WinCollect event log"
            )

        transformed = _transform_wincollect_win_log_to_standard_win_log(field_value)
        parsed = _win_event_log_parser.execute(data={field: transformed}, field=field)
        if in_place:
            set_value(data, field, parsed)
            return data
        return parsed

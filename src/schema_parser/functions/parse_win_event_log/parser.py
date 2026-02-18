import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..base import BaseFunction


@dataclass(slots=True)
class ParserState:
    """Represents the state of the parser."""

    log_json: dict[str, str] = field(default_factory=dict)
    current_section: str | None = None
    event_id: str | None = None
    last_key: str | None = None


def load_field_mapping() -> dict:
    """Loads the field mapping from the CSV file."""

    # TODO: Move this logic to logsource mapping?
    mapping = {}
    csv_path = Path(__file__).parent / "field_mapping.csv"

    with open(csv_path, encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            event_id = row["event_id"]
            sigma_field = row["sigma_field"]
            viewer_field_group = row["viewer_field_group"].strip()
            viewer_field_name = row["viewer_field_name"].strip()

            if event_id not in mapping:
                mapping[event_id] = {}
            if viewer_field_group not in mapping[event_id]:
                mapping[event_id][viewer_field_group] = {}
            mapping[event_id][viewer_field_group][viewer_field_name] = sigma_field
    return mapping


FIELDS_MAPPING_BY_EVENT_ID = load_field_mapping()
EVENT_ID_PATTERN = re.compile(r"EventCode\s*=\s*(\d+)")
KV_PATTERN = re.compile(r"^\s*([^:=\n]+?)\s*[:=]\s*(.*)$")
SECTION_PATTERN = re.compile(r"^([a-zA-Z \(\)]+?):$")


class ParseWinEventLogFunction(BaseFunction):
    """Function for parsing Windows Event Log.

    Example of the log text:

    01/01/2025 00:00:00 AM
    LogName=Security
    SourceName=Microsoft Windows security auditing.
    EventCode=4768
    EventType=0
    Type=Information
    ComputerName=EXAMPLE.COMPANY.com
    TaskCategory=Kerberos Authentication Service
    OpCode=Info
    RecordNumber=115337948
    Keywords=Audit Success
    Message=A Kerberos authentication ticket (TGT) was requested.
    Account Information:
        Account Name:       user
        Supplied Realm Name: COMPANY
        User ID:            S-1-5-21-23784103-792946567-925700815-171614
    Service Information:
        Service Name:       SERVICE
        Service ID:         S-5-21-43242361-792946567-925700815-502
    Network Information:
        Client Address:     ::ffff:10.10.40.56
        Client Port:        63564
    Additional Information:
        Ticket Options:     0x40810010
        Result Code:        0x0
        Ticket Encryption Type: 0x12
        Pre-Authentication Type: 2
    Certificate Information:
        Certificate Issuer Name:
        Certificate Serial Number:
        Certificate Thumbprint:

    """

    def execute(self, data: dict[str, Any], field: str) -> dict[str, Any]:
        log_text = data[field]
        event_id = self._get_event_id(log_text)

        lines = log_text.strip().split("\n")
        if not lines or not lines[0]:
            return {}

        state = ParserState(event_id=event_id)
        if event_id:
            state.log_json["EventID"] = event_id

        for line in lines[1:]:  # Skip the first line (timestamp)
            self._process_line(line, state)

        return state.log_json

    @staticmethod
    def _get_event_id(log_text: str) -> str | None:
        event_id_match = EVENT_ID_PATTERN.search(log_text)
        return event_id_match.group(1).strip() if event_id_match else None

    @classmethod
    def _process_line(
        cls,
        line: str,
        state: ParserState,
    ):
        stripped_line = line.strip()
        if not stripped_line:
            state.last_key = None
            return

        section_match = SECTION_PATTERN.match(stripped_line)
        if section_match:
            state.current_section = section_match.group(1).strip()
            state.last_key = None
            return

        kv_match = KV_PATTERN.match(line)
        if kv_match:
            cls._process_kv_match(line, kv_match, state)
        elif state.last_key and stripped_line:
            # This is a continuation of the previous line
            state.log_json[state.last_key] = f"{state.log_json[state.last_key]} {stripped_line}"

    @staticmethod
    def _process_kv_match(line: str, kv_match: re.Match, state: ParserState):
        key, value = kv_match.groups()
        key = key.strip()

        if key == "EventCode":
            return  # Skip the EventCode line as it's already processed

        # If a line with a kv pair is not indented, it is not part of the current section
        if not line.startswith(" ") and not line.startswith("\t"):
            state.current_section = None

        new_key = (
            FIELDS_MAPPING_BY_EVENT_ID.get(state.event_id, {})
            .get(state.current_section or "", {})
            .get(key)
        )

        # If key not in section - leave it even if it is not in the mapping
        if state.current_section:
            new_key = new_key or None
        else:
            new_key = new_key or key

        if new_key:
            value = value.strip()
            state.log_json[new_key] = value
            state.last_key = new_key

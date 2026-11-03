import pytest

from schema_parser.functions.parse_wincollect_win_event_log.parser import (
    ParseWincollectWinEventLogFunction,
    _reshape_message_region,
)

OBJECT_ACCESS_LOG = (
    "<13>Jul 13 15:18:32 HOST.sub.domain.name AgentDevice=WindowsLog\t"
    "AgentLogFile=Security\t"
    "PluginVersion=7.3.1.43\t"
    "Source=Microsoft-Windows-Security-Auditing\t"
    "Computer=HOST.sub.domain.name\t"
    "OriginatingComputer=10.10.10.10\t"
    "User=\t"
    "Domain=\t"
    "EventID=4662\t"
    "EventIDCode=4662\t"
    "EventType=8\t"
    "EventCategory=12804\t"
    "RecordNumber=3703867\t"
    "TimeGenerated=1783945048\t"
    "TimeWritten=1783945048\t"
    "Level=Log Always\t"
    "Keywords=Audit Success\t"
    "Task=SE_ADT_OBJECTACCESS_OTHER\t"
    "Opcode=Info\t"
    "Message=An operation was performed on an object.  Subject :  Security ID:  "
    "NT AUTHORITY\\LOCAL SERVICE  Account Name:  LOCAL SERVICE  Account Domain:  "
    "NT AUTHORITY  Logon ID:  0x3E5  Object:  Object Server:  LSA  Object Type:  "
    "SecretObject  Object Name:  Policy\\Secrets\\$MACHINE.ACC  Handle ID:  "
    "0x27058dfe690  Operation:  Operation Type:  Query  Accesses:  Query secret value"
    "       Access Mask:  0x2  Properties:  -  Additional Information:  "
    "Parameter 1:  -  Parameter 2:  -"
)

LOGOFF_LOG_WITH_TRAILING_PROSE = (
    "<13>Jul 13 15:18:29 hostname AgentDevice=WindowsLog\t"
    "AgentLogFile=Security\t"
    "PluginVersion=7.3.1.43\t"
    "Source=Microsoft-Windows-Security-Auditing\t"
    "Computer=hostname.sub.domain.name\t"
    "OriginatingComputer=10.10.10.10\t"
    "User=\t"
    "Domain=\t"
    "EventID=4634\t"
    "EventIDCode=4634\t"
    "EventType=8\t"
    "EventCategory=12545\t"
    "RecordNumber=76863458\t"
    "TimeGenerated=1783945108\t"
    "TimeWritten=1783945108\t"
    "Level=Log Always\t"
    "Keywords=Audit Success\t"
    "Task=SE_ADT_LOGON_LOGOFF\t"
    "Opcode=Info\t"
    "Message=An account was logged off.  Subject:  Security ID:  SUB\\USERNAME  "
    "Account Name:  Username  Account Domain:  SUB  Logon ID:  0x1ABB111  "
    "Logon Type:   3  This event is generated when a logon session is destroyed. "
    "It may be positively correlated with a logon event using the Logon ID value. "
    "Logon IDs are only unique between reboots on the same computer."
)

NO_SECTION_LOG = (
    "<13>Jul 13 15:18:32 HOSTNAME.sub.domain.name AgentDevice=WindowsLog\t"
    "AgentLogFile=Microsoft-Windows-GroupPolicy/Operational\t"
    "PluginVersion=7.3.1.43\t"
    "Source=Microsoft-Windows-GroupPolicy\t"
    "Computer=HOSTNAME.sub.domain.name\t"
    "OriginatingComputer=10.10.10.10\t"
    "User=SYSTEM\t"
    "Domain=NT AUTHORITY\t"
    "EventID=4016\t"
    "EventIDCode=4016\t"
    "EventType=4\t"
    "EventCategory=0\t"
    "RecordNumber=331846\t"
    "TimeGenerated=1783944388\t"
    "TimeWritten=1783944388\t"
    "Level=Informational\t"
    "Keywords=0x4000000000000000\t"
    "Task=None\t"
    "Opcode=Start\t"
    "Message=Starting Audit Policy Configuration Extension Processing.   "
    "List of applicable Group Policy objects: (No changes were detected.)  "
    "Audit_PC McAfee_enhance_ligging"
)

# Event 4624: several long labels are separated from their values by a single space
# (e.g. "Restricted Admin Mode: No", "Workstation Name: workstation_name") instead of
# the usual double space, because Windows pads labels to a fixed column width.
LOGON_LOG_WITH_SINGLE_SPACE_PADDED_LABELS = (
    "<13>May 08 10:45:44 microsoft.windows.test AgentDevice=WindowsLog\t"
    "AgentLogFile=Security\t"
    "PluginVersion=7.2.9.108\t"
    "Source=Microsoft-Windows-Security-Auditing\t"
    "Computer=microsoft.windows.test\t"
    "OriginatingComputer=10.0.0.2\t"
    "User=\t"
    "Domain=\t"
    "EventID=4624\t"
    "EventIDCode=4624\t"
    "EventType=8\t"
    "EventCategory=12544\t"
    "RecordNumber=649155826\t"
    "TimeGenerated=1588945541\t"
    "TimeWritten=1588945541\t"
    "Level=Log Always\t"
    "Keywords=Audit Success\t"
    "Task=SE_ADT_LOGON_LOGON\t"
    "Opcode=Info\t"
    "Message=An account was successfully logged on.  Subject:  Security ID:  "
    "NT AUTHORITY\\SYSTEM  Account Name:  account_name$  Account Domain:  "
    "account_domain  Logon ID:  0x3E7  Logon Information:  Logon Type:  10  "
    "Restricted Admin Mode: No  Virtual Account:  No  Elevated Token:  Yes  "
    "Impersonation Level:  Impersonation  New Logon:  Security ID:  "
    "account_domain\\account_name  Account Name:  account_name  Account Domain:  "
    "domain_name  Logon ID:  0x9A4D3C17  Linked Logon ID:  0x9A4D3CD6  "
    "Network Account Name: -  Network Account Domain: -  Logon GUID:  "
    "{00000000-0000-0000-0000-000000000000}  Process Information:  Process ID:  "
    "0x3e4  Process Name:  C:\\Windows\\System32\\svchost.exe  Network Information:  "
    "Workstation Name: workstation_name  Source Network Address: 10.0.0.1  "
    "Source Port:  0  Detailed Authentication Information:  Logon Process:  "
    "User32   Authentication Package: Negotiate  Transited Services: -  "
    "Package Name (NTLM only): -  Key Length:  0  This event is generated when "
    "a logon session is created. It is generated on the computer that was accessed."
)


def test_parse_wincollect_object_access_event_with_sections():
    result = ParseWincollectWinEventLogFunction().execute(
        data={"log": OBJECT_ACCESS_LOG}, field="log"
    )

    assert result["EventID"] == "4662"
    assert result["AgentLogFile"] == "Security"
    assert result["Computer"] == "HOST.sub.domain.name"
    assert result["Message"] == "An operation was performed on an object."
    # Section-scoped fields must resolve to their sigma field names via field_mapping.csv,
    # not the raw viewer field names ("Security ID", "Account Name", etc.)
    assert result["SubjectUserSid"] == "NT AUTHORITY\\LOCAL SERVICE"
    assert result["SubjectUserName"] == "LOCAL SERVICE"
    assert result["SubjectDomainName"] == "NT AUTHORITY"
    assert result["SubjectLogonId"] == "0x3E5"
    assert result["ObjectServer"] == "LSA"
    assert result["ObjectType"] == "SecretObject"
    assert result["ObjectName"] == "Policy\\Secrets\\$MACHINE.ACC"
    assert result["HandleId"] == "0x27058dfe690"
    assert result["OperationType"] == "Query"
    assert result["AccessList"] == "Query secret value"
    assert result["AccessMask"] == "0x2"
    assert result["Properties"] == "-"
    assert result["AdditionalInfo"] == "-"
    assert result["AdditionalInfo2"] == "-"


def test_parse_wincollect_logoff_event_drops_trailing_prose():
    result = ParseWincollectWinEventLogFunction().execute(
        data={"log": LOGOFF_LOG_WITH_TRAILING_PROSE}, field="log"
    )

    assert result["EventID"] == "4634"
    assert result["Message"] == "An account was logged off."
    assert result["TargetUserSid"] == "SUB\\USERNAME"
    assert result["TargetUserName"] == "Username"
    assert result["TargetDomainName"] == "SUB"
    assert result["LogonID"] == "0x1ABB111"
    # The trailing explanatory sentence must not be glued onto LogonType.
    assert result["LogonType"] == "3"


def test_parse_wincollect_event_without_sections_keeps_full_message():
    result = ParseWincollectWinEventLogFunction().execute(data={"log": NO_SECTION_LOG}, field="log")

    assert result["EventID"] == "4016"
    assert result["AgentLogFile"] == "Microsoft-Windows-GroupPolicy/Operational"
    assert result["Message"] == (
        "Starting Audit Policy Configuration Extension Processing.   "
        "List of applicable Group Policy objects: (No changes were detected.)  "
        "Audit_PC McAfee_enhance_ligging"
    )


def test_parse_wincollect_logon_event_with_single_space_padded_labels():
    # Long labels with a single space after the colon must still split into their own fields
    # instead of being glued onto the previous field's value.
    result = ParseWincollectWinEventLogFunction().execute(
        data={"log": LOGON_LOG_WITH_SINGLE_SPACE_PADDED_LABELS}, field="log"
    )

    assert result["EventID"] == "4624"
    assert result["Message"] == "An account was successfully logged on."
    assert result["SubjectUserSid"] == "NT AUTHORITY\\SYSTEM"
    assert result["SubjectUserName"] == "account_name$"
    assert result["SubjectDomainName"] == "account_domain"
    assert result["SubjectLogonId"] == "0x3E7"
    assert result["LogonType"] == "10"
    assert result["RestrictedAdminMode"] == "No"
    assert result["VirtualAccount"] == "No"
    assert result["ElevatedToken"] == "Yes"
    assert result["ImpersonationLevel"] == "Impersonation"
    assert result["TargetUserSid"] == "account_domain\\account_name"
    assert result["TargetUserName"] == "account_name"
    assert result["TargetDomainName"] == "domain_name"
    assert result["TargetLogonId"] == "0x9A4D3C17"
    assert result["TargetLinkedLogonId"] == "0x9A4D3CD6"
    assert result["TargetOutboundUserName"] == "-"
    assert result["TargetOutboundDomainName"] == "-"
    assert result["LogonGuid"] == "{00000000-0000-0000-0000-000000000000}"
    assert result["ProcessId"] == "0x3e4"
    assert result["ProcessName"] == "C:\\Windows\\System32\\svchost.exe"
    assert result["WorkstationName"] == "workstation_name"
    assert result["IpAddress"] == "10.0.0.1"
    assert result["IpPort"] == "0"
    assert result["LogonProcessName"] == "User32"
    assert result["AuthenticationPackageName"] == "Negotiate"
    assert result["TransmittedServices"] == "-"
    assert result["LmPackageName"] == "-"
    assert result["KeyLength"] == "0"


def test_parse_wincollect_event_id_code_only():
    """Some WinCollect logs emit EventIDCode without EventID."""
    log = (
        "<13>Jul 13 15:18:32 HOST.sub.domain.name AgentDevice=WindowsLog\t"
        "AgentLogFile=Security\t"
        "Source=Microsoft-Windows-Security-Auditing\t"
        "Computer=HOST.sub.domain.name\t"
        "EventIDCode=4662\t"
        "EventType=8\t"
        "Message=An operation was performed on an object."
    )
    result = ParseWincollectWinEventLogFunction().execute(data={"log": log}, field="log")

    assert result["EventID"] == "4662"
    assert result["Message"] == "An operation was performed on an object."


def test_reshape_returns_message_unchanged_when_no_structured_fields():
    # No "  Key:  " delimiter anywhere -> the message is free-form and must be returned as-is.
    message = "Message=No structured fields here at all."
    assert _reshape_message_region(message) == message


def test_reshape_leaves_prose_with_single_spaced_colon_untouched():
    # A colon inside prose ("objects: (No changes...)") uses single spaces, so it must not be
    # mistaken for a "  Key:  " field delimiter and the whole message stays intact.
    message = (
        "Message=Starting Processing.   List of applicable Group Policy "
        "objects: (No changes were detected.)  Audit_PC"
    )
    assert _reshape_message_region(message) == message


def test_reshape_splits_section_into_header_and_indented_fields():
    message = "Message=An event happened.  Subject:  Security ID:  S-1-5-18  Account Name:  SYSTEM"
    assert _reshape_message_region(message) == (
        "Message=An event happened.\n"
        "Subject:\n"
        "    Security ID:  S-1-5-18\n"
        "    Account Name:  SYSTEM\n"
    )


def test_reshape_handles_single_space_packed_key_value():
    # "Restricted Admin Mode: No" has a single space after the colon (not the usual double
    # space) but is still a real field and must be split onto its own indented line.
    message = "Message=Header text.  Logon Type:  3  Restricted Admin Mode: No"
    assert _reshape_message_region(message) == (
        "Message=Header text.\n    Logon Type:  3\n    Restricted Admin Mode: No\n"
    )


def test_reshape_keeps_windows_path_as_value_not_key():
    # "C:\\Windows\\..." contains a colon but is a drive-letter path value, not a field key.
    message = "Message=Info.  Process Name:  C:\\Windows\\System32\\svchost.exe  Process ID:  0x4"
    assert _reshape_message_region(message) == (
        "Message=Info.\n"
        "    Process Name:  C:\\Windows\\System32\\svchost.exe\n"
        "    Process ID:  0x4\n"
    )


def test_reshape_isolates_trailing_prose_behind_blank_line():
    # A trailing explanatory sentence (no colon) must be pushed behind a blank line so
    # parse_win_event_log does not glue it onto the previous field's value.
    message = (
        "Message=Account logged off.  Logon Type:  3  "
        "This event is generated when a logon session is destroyed."
    )
    assert _reshape_message_region(message) == (
        "Message=Account logged off.\n"
        "    Logon Type:  3\n"
        "\n"
        "This event is generated when a logon session is destroyed.\n"
    )


def test_reshape_detects_section_when_followed_by_packed_key():
    # "Logon Information:" is a section header because the next token is itself a field.
    message = "Message=Evt.  Logon Information:  Restricted Admin Mode: No"
    assert _reshape_message_region(message) == (
        "Message=Evt.\nLogon Information:\n    Restricted Admin Mode: No\n"
    )


def test_reshape_emits_dangling_trailing_colon_token_as_is():
    # A key/section token with no following value (end of message) is emitted on its own line.
    message = "Message=Evt.  Logon Type:  3  Dangling Section:"
    assert _reshape_message_region(message) == (
        "Message=Evt.\n    Logon Type:  3\nDangling Section:\n"
    )


def test_parse_wincollect_win_event_log_missing_field_returns_empty_dict():
    result = ParseWincollectWinEventLogFunction().execute(data={}, field="log")
    assert result == {}


def test_parse_wincollect_win_event_log_non_string_field_raises():
    with pytest.raises(ValueError):
        ParseWincollectWinEventLogFunction().execute(data={"log": 12345}, field="log")


def test_parse_wincollect_win_event_log_in_place_keeps_other_fields():
    data = {"@timestamp": "2026-07-13T12:18:44Z", "event": {"original": OBJECT_ACCESS_LOG}}
    result = ParseWincollectWinEventLogFunction().execute(
        data=data, field="event.original", in_place=True
    )
    assert result["@timestamp"] == "2026-07-13T12:18:44Z"
    assert result["event"]["original"]["EventID"] == "4662"

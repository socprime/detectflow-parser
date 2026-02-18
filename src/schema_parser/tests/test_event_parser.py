from schema_parser.functions.parse_win_event_log.parser import ParseWinEventLogFunction


def test_parse_splunk_event_log_text_4648():
    log_content = """
    01/01/2025 10:00:00 AM
    LogName=Security
    EventCode=4648
    EventType=0
    ComputerName=example.com
    SourceName=Microsoft Windows security auditing.
    Type=Information
    RecordNumber=12345
    Keywords=Audit Success
    TaskCategory=Logon
    OpCode=Info
    Message=A logon was attempted using explicit credentials.

    Subject:
        Security ID:        NT AUTHORITY\\SYSTEM
        Account Name:        EXAMPLE$
        Account Domain:        EXAMPLE
        Logon ID:        0x3E7
        Logon GUID:        {00000000-0000-0000-0000-000000000000}

    Account Whose Credentials Were Used:
        Account Name:        test_user
        Account Domain:        EXAMPLE
        Logon GUID:        {11111111-1111-1111-1111-111111111111}

    Target Server:
        Target Server Name:    localhost
        Additional Information:    localhost

    Process Information:
        Process ID:        0x368
        Process Name:        C:\\Windows\\System32\\lsass.exe

    Network Information:
        Network Address:    10.10.10.10
        Port:            57200
    """
    expected_result = {
        "EventID": "4648",
        "LogName": "Security",
        "EventType": "0",
        "ComputerName": "example.com",
        "SourceName": "Microsoft Windows security auditing.",
        "Type": "Information",
        "RecordNumber": "12345",
        "Keywords": "Audit Success",
        "TaskCategory": "Logon",
        "OpCode": "Info",
        "Message": "A logon was attempted using explicit credentials.",
        "SubjectUserSid": "NT AUTHORITY\\SYSTEM",
        "SubjectUserName": "EXAMPLE$",
        "SubjectDomainName": "EXAMPLE",
        "SubjectLogonId": "0x3E7",
        "LogonGuid": "{00000000-0000-0000-0000-000000000000}",
        "TargetUserName": "test_user",
        "TargetDomainName": "EXAMPLE",
        "TargetLogonGuid": "{11111111-1111-1111-1111-111111111111}",
        "TargetServerName": "localhost",
        "TargetInfo": "localhost",
        "ProcessId": "0x368",
        "ProcessName": "C:\\Windows\\System32\\lsass.exe",
        "IpAddress": "10.10.10.10",
        "IpPort": "57200",
    }

    parsed_log = ParseWinEventLogFunction().execute(
        data={"log_text": log_content}, field="log_text"
    )
    assert parsed_log == expected_result


def test_parse_splunk_event_log_text_no_section():
    log_content = """
    07/18/2025 11:09:59 AM
    LogName=Security
    EventCode=4648
    ComputerName=example.com
    """
    expected_result = {
        "EventID": "4648",
        "LogName": "Security",
        "ComputerName": "example.com",
    }
    parsed_log = ParseWinEventLogFunction().execute(
        data={"log_text": log_content}, field="log_text"
    )
    assert parsed_log == expected_result


def test_parse_splunk_event_log_text_empty_log():
    log_content = ""
    expected_result = {}
    parsed_log = ParseWinEventLogFunction().execute(
        data={"log_text": log_content}, field="log_text"
    )
    assert parsed_log == expected_result


def test_parse_splunk_event_log_text_no_event_id():
    log_content = """
    07/18/2025 11:09:59 AM
    LogName=Security
    ComputerName=example.com
    """
    expected_result = {
        "LogName": "Security",
        "ComputerName": "example.com",
    }
    parsed_log = ParseWinEventLogFunction().execute(
        data={"log_text": log_content}, field="log_text"
    )
    assert parsed_log == expected_result


def test_multiline_values():
    text = """01/01/2025 01:01:01 PM
LogName=Security
EventCode=4662
EventType=0
ComputerName=example.com
SourceName=Microsoft Windows security auditing.
Type=Information
RecordNumber=12345
Keywords=Audit Success
TaskCategory=Other Object Access Events
OpCode=Info
Message=An operation was performed on an object.

Subject :
    Security ID:        S-1-5-18
    Account Name:        example
    Account Domain:        7logs
    Logon ID:        0x3E7

Object:
    Object Server:        WMI
    Object Type:        WMI Namespace
    Object Name:        ROOT\\CIMV2\\Security\\MicrosoftVolumeEncryption
    Handle ID:        0x0

Operation:
    Operation Type:        Object Access
    Accesses:        Unknown specific access (bit 0)
                Unknown specific access (bit 1)

    Access Mask:        0x3
    Properties:        -

Additional Information:
    Parameter 1:        test1
    Parameter 2:        test2
"""

    expected_result = {
        "EventID": "4662",
        "LogName": "Security",
        "EventType": "0",
        "ComputerName": "example.com",
        "SourceName": "Microsoft Windows security auditing.",
        "Type": "Information",
        "RecordNumber": "12345",
        "Keywords": "Audit Success",
        "TaskCategory": "Other Object Access Events",
        "OpCode": "Info",
        "Message": "An operation was performed on an object.",
        "SubjectUserSid": "S-1-5-18",
        "SubjectUserName": "example",
        "SubjectDomainName": "7logs",
        "SubjectLogonId": "0x3E7",
        "ObjectServer": "WMI",
        "ObjectType": "WMI Namespace",
        "ObjectName": "ROOT\\CIMV2\\Security\\MicrosoftVolumeEncryption",
        "HandleId": "0x0",
        "OperationType": "Object Access",
        "AccessList": "Unknown specific access (bit 0) Unknown specific access (bit 1)",
        "AccessMask": "0x3",
        "Properties": "-",
        "AdditionalInfo": "test1",
        "AdditionalInfo2": "test2",
    }
    parsed_log = ParseWinEventLogFunction().execute(data={"log_text": text}, field="log_text")
    assert parsed_log == expected_result


def test_equal_kv_values_follows_colon_cv_values():
    text = """01/01/2025 01:01:01 PM
LogName=Security
EventCode=4662
EventType=0
SourceName=Microsoft Windows security auditing.
Type=Information
RecordNumber=12345
Keywords=Audit Success
TaskCategory=Other Object Access Events
OpCode=Info
Message=An operation was performed on an object.

Subject :
    Security ID:        S-1-5-18
    Account Name:        example
    Account Domain:        7logs
    Logon ID:        0x3E7

Object:
    Object Server:        WMI
    Object Type:        WMI Namespace
    Object Name:        ROOT\\CIMV2\\Security\\MicrosoftVolumeEncryption
    Handle ID:        0x0

Operation:
    Operation Type:        Object Access
    Accesses:        Unknown specific access (bit 0)
                Unknown specific access (bit 1)

    Access Mask:        0x3
    Properties:        -

Additional Information:
    Parameter 1:        test1
    Parameter 2:        test2
ComputerName=example.com
"""

    expected_result = {
        "EventID": "4662",
        "LogName": "Security",
        "EventType": "0",
        "ComputerName": "example.com",
        "SourceName": "Microsoft Windows security auditing.",
        "Type": "Information",
        "RecordNumber": "12345",
        "Keywords": "Audit Success",
        "TaskCategory": "Other Object Access Events",
        "OpCode": "Info",
        "Message": "An operation was performed on an object.",
        "SubjectUserSid": "S-1-5-18",
        "SubjectUserName": "example",
        "SubjectDomainName": "7logs",
        "SubjectLogonId": "0x3E7",
        "ObjectServer": "WMI",
        "ObjectType": "WMI Namespace",
        "ObjectName": "ROOT\\CIMV2\\Security\\MicrosoftVolumeEncryption",
        "HandleId": "0x0",
        "OperationType": "Object Access",
        "AccessList": "Unknown specific access (bit 0) Unknown specific access (bit 1)",
        "AccessMask": "0x3",
        "Properties": "-",
        "AdditionalInfo": "test1",
        "AdditionalInfo2": "test2",
    }
    parsed_log = ParseWinEventLogFunction().execute(data={"log_text": text}, field="log_text")
    assert parsed_log == expected_result


def test_parse_splunk_event_log_text_4688_special_chars_in_section():
    log_content = """
    01/01/2025 10:00:00 AM
    LogName=Security
    EventCode=4688
    EventType=0
    ComputerName=example.com
    SourceName=Microsoft Windows security auditing.
    Type=Information
    RecordNumber=12345
    Keywords=Audit Success
    TaskCategory=Process Creation
    OpCode=Info
    Message=A new process has been created.

    (Creator) Subject:
        Security ID:        NT AUTHORITY\\SYSTEM
        Account Name:        EXAMPLE$
        Account Domain:        EXAMPLE
        Logon ID:        0x3E7

    Process Information:
        New Process ID:        0x1234
        New Process Name:    C:\\Windows\\System32\\notepad.exe
        Token Elevation Type:    %%1936
        Creator Process ID:    0x5678
        Process Command Line:    notepad.exe
        Creator Process Name:    C:\\Windows\\System32\\explorer.exe
        Mandatory Label:    S-1-16-12288

    Target Subject:
        Security ID:        NULL SID
        Account Name:        -
        Account Domain:        -
        Logon ID:        0x0
    """
    expected_result = {
        "EventID": "4688",
        "LogName": "Security",
        "EventType": "0",
        "ComputerName": "example.com",
        "SourceName": "Microsoft Windows security auditing.",
        "Type": "Information",
        "RecordNumber": "12345",
        "Keywords": "Audit Success",
        "TaskCategory": "Process Creation",
        "OpCode": "Info",
        "Message": "A new process has been created.",
        "SubjectUserSid": "NT AUTHORITY\\SYSTEM",
        "SubjectUserName": "EXAMPLE$",
        "SubjectDomainName": "EXAMPLE",
        "SubjectLogonId": "0x3E7",
        "NewProcessId": "0x1234",
        "NewProcessName": "C:\\Windows\\System32\\notepad.exe",
        "TokenElevationType": "%%1936",
        "ProcessId": "0x5678",
        "CommandLine": "notepad.exe",
        "ParentProcessName": "C:\\Windows\\System32\\explorer.exe",
        "MandatoryLabel": "S-1-16-12288",
        "TargetUserSid": "NULL SID",
        "TargetUserName": "-",
        "TargetDomainName": "-",
        "TargetLogonId": "0x0",
    }

    parsed_log = ParseWinEventLogFunction().execute(
        data={"log_text": log_content}, field="log_text"
    )
    assert parsed_log == expected_result


def test_field_without_section_parsing_in_event_4739():
    log_content = """
    01/01/2025 10:00:00 AM
    LogName=Security
    EventCode=4739
    EventType=0
    ComputerName=example.com

    Change Type:            change_type_value

    Subject:
        Security ID:        security_id_value
        Account Name:       account_name_value
        Account Domain:     account_domain_value
        Logon ID:           logon_id_value

    Domain:
        Domain Name:        domain_name_value
        Domain ID:          domain_id_value

    Changed Attributes:
        Min. Password Age:  min_password_age_value
        Max. Password Age:  max_password_age_value
    """
    expected_result = {
        "EventID": "4739",
        "LogName": "Security",
        "EventType": "0",
        "ComputerName": "example.com",
        "DomainPolicyChanged": "change_type_value",
        "SubjectUserSid": "security_id_value",
        "SubjectUserName": "account_name_value",
        "SubjectDomainName": "account_domain_value",
        "SubjectLogonId": "logon_id_value",
        "DomainName": "domain_name_value",
        "DomainSid": "domain_id_value",
        "MinPasswordAge": "min_password_age_value",
        "MaxPasswordAge": "max_password_age_value",
    }
    parsed_log = ParseWinEventLogFunction().execute(
        data={"log_text": log_content}, field="log_text"
    )
    assert parsed_log == expected_result

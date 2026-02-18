parser_query_example = """parse_json(field="payload")
| regex(field="raw", pattern=regex_pattern)
| rename(from="event.user", to="user.name")
| drop(fields="event.count")
| set(field="event.type", value="http_access")"""


parser_query_result = {
    "steps": ["parse_json", "regex", "rename", "drop", "set"],
    "args": {
        "parse_json": {
            "field": "raw"
        },
        "regex": {
            "pattern": "[a-zA-Z0-9.]+"
        },
        "rename": {
            "from": "event.user",
            "to": "user.name"
        },
        "drop": {
            "fields": "event.count"
        },
        "set": {
            "field": "event.type",
            "value": "http_access"
        }
    }
}

"""
Constants defining supported and unsupported Sigma features.

Based on apache-flink-tdm sigma_parser.py validation logic.

Supported features:
- Modifiers: contains, startswith, endswith, all (combinable)
- Conditions: and, or, not, all of X*, 1 of X*, all of them, 1 of them, parentheses
- Values: strings, lists, wildcards (*, ?)

Unsupported features:
- Modifiers: exists, cased, neq, windash, re, base64*, utf16*, wide, lt, lte, gt, gte,
             cidr, expand, fieldref
- Correlation rules, aggregations, thresholds, temporal correlation
"""

# Supported modifiers that can be combined
SUPPORTED_MODIFIERS: frozenset[str] = frozenset(
    {
        "contains",
        "startswith",
        "endswith",
        "all",
    }
)

# Unsupported modifiers - these will cause validation to fail
UNSUPPORTED_MODIFIERS: frozenset[str] = frozenset(
    {
        # Type modifiers
        "exists",
        "cased",
        "neq",
        # Transformation modifiers
        "windash",
        "re",
        "base64",
        "base64offset",
        "utf16",
        "utf16le",
        "utf16be",
        "wide",
        # Comparison modifiers
        "lt",
        "lte",
        "gt",
        "gte",
        # Network modifiers
        "cidr",
        # Special modifiers
        "expand",
        "fieldref",
    }
)

# All known modifiers (for reference)
ALL_KNOWN_MODIFIERS: frozenset[str] = SUPPORTED_MODIFIERS | UNSUPPORTED_MODIFIERS

# Supported condition operators
SUPPORTED_CONDITION_OPERATORS: frozenset[str] = frozenset(
    {
        "and",
        "or",
        "not",
    }
)

# Supported condition keywords/patterns
SUPPORTED_CONDITION_KEYWORDS: frozenset[str] = frozenset(
    {
        "all of",
        "1 of",
        "all of them",
        "1 of them",
    }
)

# Unsupported rule types
UNSUPPORTED_RULE_TYPES: frozenset[str] = frozenset(
    {
        "correlation",
    }
)

# Unsupported condition features (aggregations, etc.)
UNSUPPORTED_CONDITION_FEATURES: tuple[str, ...] = (
    # Aggregation functions
    "count(",
    "sum(",
    "avg(",
    "min(",
    "max(",
    # Time-based features
    "near",
    "timespan",
    # Threshold conditions
    ">",
    "<",
    ">=",
    "<=",
    "==",
    "!=",
    # Pipe operator for post-processing
    "|",
)

# Valid characters pattern for condition expression (after normalizing all/1 of)
# Allows: alphanumeric, underscore, space, parentheses, asterisk, question mark
VALID_CONDITION_CHARS_PATTERN = r"^[a-zA-Z0-9_ \(\)\?\*]+$"

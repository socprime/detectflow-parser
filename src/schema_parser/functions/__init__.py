from .drop import DropFunction
from .extract import ExtractFunction
from .parse_json import ParseJsonFunction
from .parse_win_event_log import ParseWinEventLogFunction
from .regex import RegexFunction
from .rename import RenameFunction
from .set import SetFunction

CORE_FUNCTIONS = {
    "parse_json": ParseJsonFunction(),
    "regex": RegexFunction(),
    "rename": RenameFunction(),
    "drop": DropFunction(),
    "set": SetFunction(),
    "parse_win_event_log": ParseWinEventLogFunction(),
    "extract": ExtractFunction(),
}

__all__ = [
    "FUNCTIONS",
    "ParseJsonFunction",
    "RegexFunction",
    "RenameFunction",
    "DropFunction",
    "SetFunction",
    "ParseWinEventLogFunction",
    "ExtractFunction",
]

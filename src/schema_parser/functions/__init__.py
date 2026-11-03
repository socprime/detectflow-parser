from .drop import DropFunction
from .extract import ExtractFunction
from .list_to_dict import ListToDictFunction
from .parse_json import ParseJsonFunction
from .parse_kv import ParseKvFunction
from .parse_leef import ParseLeefFunction
from .parse_win_event_log import ParseWinEventLogFunction
from .parse_wincollect_win_event_log import ParseWincollectWinEventLogFunction
from .parse_xml import ParseXmlFunction
from .regex import RegexFunction
from .rename import RenameFunction
from .set import SetFunction

CORE_FUNCTIONS = {
    "parse_json": ParseJsonFunction(),
    "parse_kv": ParseKvFunction(),
    "parse_leef": ParseLeefFunction(),
    "parse_xml": ParseXmlFunction(),
    "regex": RegexFunction(),
    "rename": RenameFunction(),
    "drop": DropFunction(),
    "set": SetFunction(),
    "parse_win_event_log": ParseWinEventLogFunction(),
    "parse_wincollect_win_event_log": ParseWincollectWinEventLogFunction(),
    "extract": ExtractFunction(),
    "list_to_dict": ListToDictFunction(),
}

__all__ = [
    "CORE_FUNCTIONS",
    "ParseJsonFunction",
    "ParseKvFunction",
    "ParseLeefFunction",
    "ParseXmlFunction",
    "RegexFunction",
    "RenameFunction",
    "DropFunction",
    "SetFunction",
    "ParseWinEventLogFunction",
    "ParseWincollectWinEventLogFunction",
    "ExtractFunction",
    "ListToDictFunction",
]

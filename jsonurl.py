from typing import Any
from urllib.parse import quote_plus


def dumps(arg: Any) -> str:
    if arg is True:
        return "true"
    if arg is False:
        return "false"
    if arg is None:
        return "null"
    if isinstance(arg, str):
        if arg == "true":
            return "'true'"
        if arg == "false":
            return "'false'"
        if arg == "null":
            return "'null'"
        return quote_plus(arg)
    if isinstance(arg, int):
        return str(arg)
    if isinstance(arg, list):
        return "(" + ",".join(dumps(x) for x in arg) + ")"
    if isinstance(arg, dict):
        return "(" + ",".join(dumps(k) + ":" + dumps(v) for k, v in arg.items()) + ")"
    raise ValueError(f"Bad value {arg!r} of type {type(arg)}")

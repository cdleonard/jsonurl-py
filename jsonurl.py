import re
from typing import Any, Tuple
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


RE_NUMBER = re.compile("^[0-9]+$")
RE_UNRESERVED = re.compile("[a-zA-Z0-9-_.~]")


class ParseError(Exception):
    pass


def _parse_hexdigit(arg: str, pos: int) -> int:
    char = arg[pos]
    if char >= "0" and char <= "9":
        return ord(char) - ord("0")
    elif char >= "a" and char <= "f":
        return ord(char) - ord("a") + 10
    elif char >= "A" and char <= "F":
        return ord(char) - ord("a") + 10
    else:
        raise ParseError(f"Invalid hex digit {char!r} at pos {pos}")


def _parse_percent(arg: str, pos: int) -> Tuple[str, int]:
    arr = []
    while pos < len(arg) and arg[pos] == "%":
        if pos + 2 >= len(arg):
            raise ParseError("Unterminated percent")
        arr.append(_parse_hexdigit(arg, pos + 1) * 16 + _parse_hexdigit(arg, pos + 2))
        pos += 3
    return bytes(arr).decode("utf-8"), pos


def _is_unreserved(char: str) -> bool:
    return RE_UNRESERVED.match(char) is not None


def _convert_unquoted_atom(arg: str) -> Any:
    if arg == "null":
        return None
    if arg == "true":
        return True
    if arg == "false":
        return False
    if re.match(RE_NUMBER, arg):
        return int(arg)
    else:
        return arg


def _parse_atom(arg: str, pos: int) -> Tuple[Any, int]:
    """Parse an atom: string, int, bool, null"""
    ret = ""
    while True:
        if pos == len(arg):
            return _convert_unquoted_atom(ret), pos
        char = arg[pos]
        if arg[pos] == "%":
            enc, pos = _parse_percent(arg, pos)
            ret += enc
        elif arg[pos] == "+":
            ret += " "
            pos += 1
        elif _is_unreserved(char):
            ret += char
            pos += 1
        else:
            return _convert_unquoted_atom(ret), pos


def _parse_list(arg: str, pos: int, first_element: Any) -> Tuple[list, int]:
    """Parse a list. pos points after the first item"""
    ret = [first_element]
    while True:
        if pos == len(arg):
            raise ParseError(f"Unterminated list")
        char = arg[pos]
        if char == ")":
            return ret, pos + 1
        if char == ",":
            pos += 1
            item, pos = _parse_any(arg, pos)
            ret.append(item)
            continue
        raise ParseError(f"Unexpected char {char!r} at pos {pos} in list")


def _parse_dict(arg: str, pos: int, first_key: Any) -> Tuple[list, int]:
    first_val, pos = _parse_atom(arg, pos)
    ret = {first_key: first_val}
    while True:
        if pos == len(arg):
            raise ParseError(f"Unterminated dict")
        char = arg[pos]
        if char == ")":
            return ret, pos + 1
        key, pos = _parse_atom(arg, pos)
        if pos == len(arg):
            raise ParseError(f"Unterminated dict, missing value")
        char = arg[pos]
        if char != ",":
            raise ParseError(f"Unexpected char {char!r} at pos {pos}, expected ,")
        val, pos = _parse_any(arg, pos)
        ret[key] = val


def _parse_compound(arg: str, pos: int) -> Tuple[Any, int]:
    """Parse a compound: list or dict"""
    val, pos = _parse_atom(arg, pos)
    if pos == len(arg):
        raise ParseError("Unterminated compound")
    char = arg[pos]
    if char == ":":
        pos += 1
        return _parse_dict(arg, pos, val)
    if char == ",":
        return _parse_list(arg, pos, val)
    raise ParseError(f"Unexpected char {char} at pos {pos}, expected , or :")


def _parse_any(arg: str, pos: int) -> Tuple[Any, int]:
    if arg[pos] == "(":
        return _parse_compound(arg, pos + 1)
    else:
        return _parse_atom(arg, pos)


def _parse_top(arg: str, pos: int) -> Any:
    ret, pos = _parse_any(arg, pos)
    if pos != len(arg):
        char = arg[pos]
        raise ParseError(f"Expected end of input at {pos}, got {char!r}")
    return ret


def loads(arg: str):
    return _parse_top(arg, 0)

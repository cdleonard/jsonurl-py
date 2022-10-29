#! /usr/bin/env python3

"""
Python implementation of jsonurl, an alternative format for JSON data model

See https://jsonurl.org/ and https://github.com/jsonurl/specification/
"""

__version__ = "0.4.0"

import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, overload
from urllib.parse import quote_plus

if sys.hexversion >= 0x030A0000:  # pragma: no cover

    def _dataclass_kwonly(*a, **kw):
        return dataclass(*a, **kw, kw_only=True)  # type: ignore

else:
    _dataclass_kwonly = dataclass


@_dataclass_kwonly
class CommonOpts:
    """
    Common options for both `dumps` and `loads`
    """

    implied_list: bool = False
    """
    Implied-Array mode: Omit parantheses and assume data is list

    See `spec section 2.9.1 <https://github.com/jsonurl/specification/#291-implied-arrays>`_
    """

    implied_dict: bool = False
    """
    Implied-Object mode: Omit parantheses and assume data is dict

    See `spec section 2.9.2 <https://github.com/jsonurl/specification/#292-implied-objects>`_
    """

    distinguish_empty_list_dict: bool = False
    """Distinguish between empty list and empty dict

    Use ``(:)`` for empty dict and ``()`` for empty list as per `spec section 2.9.5
    <https://github.com/jsonurl/specification/#295-empty-objects-and-arrays>`_
    """

    aqf: bool = False
    """Address bar Query string Friendly

    Use ``!`` quoting instead of ``'`` as per `spec section 2.9.6
    <https://github.com/jsonurl/specification/#296-address-bar-query-string-friendly>`_
    """


@_dataclass_kwonly
class DumpOpts(CommonOpts):
    """
    Options for `jsonurl_py.dumps`
    """

    safe: str = ""
    """
    Additional characters considered safe and not requiring percent-encoding.

    This is similar to the safe argument to `urllib.parse.quote_plus`.

    By default only the characters ``[a-zA-Z0-9_.-~]`` are safe. Additional
    characters that can be marked safe are: ``!$*/;?@``. In AQF mode the
    characters "'" can also be marked as safe.

    In AQF mode the characters `!(),:` are considered safe by default so that
    output is readable but on input they are also recognized in encoded form.
    """


def _dump_list_data(arg: Any, opts: DumpOpts) -> str:
    return ",".join(_dump_any(x, opts) for x in arg)


def _dump_dict_data(arg: Any, opts: DumpOpts) -> str:
    return ",".join(
        _dump_any(k, opts) + ":" + _dump_any(v, opts) for k, v in arg.items()
    )


def _dump_str(arg: str, opts: DumpOpts) -> str:
    if opts.aqf:
        if arg == "true":
            return "!true"
        if arg == "false":
            return "!false"
        if arg == "null":
            return "!null"
        if arg == "":
            return "!e"
        if RE_NUMBER.match(arg):
            return "!" + arg
        return quote_plus(arg, safe=opts.safe + "(),:!").translate(
            {
                ord("!"): "!!",
                ord("("): "!(",
                ord(")"): "!)",
                ord(","): "!,",
                ord(":"): "!:",
            }
        )
    else:
        if arg == "true":
            return "'true'"
        if arg == "false":
            return "'false'"
        if arg == "null":
            return "'null'"
        if arg == "":
            return "''"
        if RE_NUMBER.match(arg):
            return "'" + arg + "'"
        return quote_plus(arg, safe=opts.safe)


def _dump_any(arg: Any, opts: DumpOpts) -> str:
    if arg is True:
        return "true"
    if arg is False:
        return "false"
    if arg is None:
        return "null"
    if isinstance(arg, str):
        return _dump_str(arg, opts)
    if isinstance(arg, int):
        return str(arg)
    if isinstance(arg, float):
        return str(arg)
    if isinstance(arg, list):
        return "(" + _dump_list_data(arg, opts) + ")"
    if isinstance(arg, dict):
        if len(arg) == 0 and opts.distinguish_empty_list_dict:
            return "(:)"
        else:
            return "(" + _dump_dict_data(arg, opts) + ")"
    raise TypeError(f"Bad value {arg!r} of type {type(arg)}")


@overload
def dumps(arg: Any, opts: Optional[DumpOpts] = None) -> str:
    ...


@overload
def dumps(
    arg: Any,
    *,
    implied_list: bool = False,
    implied_dict: bool = False,
    aqf: bool = False,
    safe: str = "",
    distinguish_empty_list_dict: bool = False,
) -> str:
    ...


def dumps(arg: Any, opts=None, **kw) -> str:
    """
    Convert a json object into a jsonurl string

    Options can be passed as a `DumpOpts` object or as individual keyword arguments.
    """
    if opts is None:
        opts = DumpOpts(**kw)
    elif kw:
        raise ValueError("Either opts or kw, not both")
    check_can_mark_safe(opts.safe, opts.aqf)

    if opts.implied_dict:
        return _dump_dict_data(arg, opts)
    if opts.implied_list:
        return _dump_list_data(arg, opts)
    return _dump_any(arg, opts)


def check_can_mark_safe(safe: str, aqf=False):
    """Check if a string can be marked as safe for jsonurl"""
    for c in safe:
        if c in "!$*/;?@":
            continue
        if aqf and c == "'":
            continue
        raise ValueError(f"Can't mark character {c!r} as safe")


@_dataclass_kwonly
class LoadOpts(CommonOpts):
    """
    Options for `loads` method
    """


RE_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?$")
RE_INT_NUMBER = re.compile(r"^-?\d+$")


class ParseError(Exception):
    pass


def _load_hexdigit(arg: str, pos: int) -> int:
    char = arg[pos]
    if char >= "0" and char <= "9":
        return ord(char) - ord("0")
    elif char >= "a" and char <= "f":
        return ord(char) - ord("a") + 10
    elif char >= "A" and char <= "F":
        return ord(char) - ord("A") + 10
    else:
        raise ParseError(f"Invalid hex digit {char!r} at pos {pos}")


def _load_percent(arg: str, pos: int) -> Tuple[str, int]:
    arr = []
    while pos < len(arg) and arg[pos] == "%":
        if pos + 2 >= len(arg):
            raise ParseError(f"Unterminated percent at pos {pos}")
        arr.append(_load_hexdigit(arg, pos + 1) * 16 + _load_hexdigit(arg, pos + 2))
        pos += 3
    return bytes(arr).decode("utf-8"), pos


_UNENCODED_CHAR_LIST = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~!$*/;?@"
)


def _is_unencoded(char: str) -> bool:
    """If one of the sharacters listed as "unencoded" in jsonurl spec"""
    return char in _UNENCODED_CHAR_LIST


_AQF_PARTIAL_DECODE_SET = set([ord("("), ord(")"), ord(","), ord(":"), ord("!")])


def _partial_decode_aqf(arg: str) -> str:
    """Perform partial percent decoding for AQF

    Affects (),:!

    All the characters involved are ascii so they can't be part of a multi-byte
    character. Overlong encodings don't need handling either, they will reach
    _load_percent and be rejected by the python utf-8 decoder.

    This is done so that the rest of the parser can check for structural
    characters without worrying about percent enconding.
    """
    ret = ""
    spos = 0
    while True:
        epos = arg.find("%", spos)
        if epos == -1:
            return ret + arg[spos:]
        if epos + 2 >= len(arg):
            raise ParseError(f"Unterminated percent at pos {epos}")
        val = _load_hexdigit(arg, epos + 1) * 16 + _load_hexdigit(arg, epos + 2)
        if val in _AQF_PARTIAL_DECODE_SET:
            ret += arg[spos:epos] + chr(val)
            spos = epos + 3
        else:
            ret += arg[spos : epos + 3]
            spos = epos + 3


def _unquote_aqf(arg: str) -> str:
    ret = ""
    spos = 0
    while True:
        epos = arg.find("!", spos)
        if epos == -1:
            return ret + arg[spos:]
        if epos == len(arg) - 1:
            raise ParseError(f"Invalid trailing ! in atom {arg!r}")
        eval = arg[epos + 1]
        if eval in "():,0123456789+-!fnt":
            ret += arg[spos:epos] + eval
            spos = epos + 2
        else:
            raise ParseError(f"Invalid !-escaped char {hex(ord(eval))}")


def _convert_unquoted_atom(arg: Optional[str], decstr: str, opts: LoadOpts) -> Any:
    if arg is not None:
        if arg == "null":
            return None
        if arg == "true":
            return True
        if arg == "false":
            return False
        if re.match(RE_NUMBER, arg):
            if re.match(RE_INT_NUMBER, arg):
                return int(arg)
            else:
                return float(arg)
    if opts.aqf:
        if decstr == "!e":
            return ""
        else:
            return _unquote_aqf(decstr)
    else:
        return decstr


def _load_qstr(arg: str, pos: int) -> Tuple[str, int]:
    """Parse a quoted string until the closing '"""
    ret = ""
    while True:
        if pos == len(arg):
            raise ParseError(f"Unterminated quoted string")
        char = arg[pos]
        if char == "%":
            enc, pos = _load_percent(arg, pos)
            ret += enc
        elif char == "+":
            ret += " "
            pos += 1
        elif char == "'":
            return ret, pos + 1
        elif _is_unencoded(char) or char in "(,:)":
            ret += char
            pos += 1
        else:
            raise ParseError(f"Unexpected char {char!r} in quoted string at pos {pos}")


def _load_atom(arg: str, pos: int, opts: LoadOpts) -> Tuple[Any, int]:
    """Parse an atom: string, int, bool, null"""
    # on-the-fly decoding into ret
    ret = ""
    # raw contains the string without decoding to check for unquoted atoms.
    raw: Optional[str] = ""
    if pos == len(arg):
        raise ParseError(f"Unexpected empty value at pos {pos}")
    char = arg[pos]
    if char == "'" and not opts.aqf:
        return _load_qstr(arg, pos + 1)
    while True:
        if pos == len(arg):
            # We know string is not empty because we checked it before aposthrophe
            assert len(ret)
            return _convert_unquoted_atom(raw, ret, opts), pos
        char = arg[pos]
        if char == "%":
            enc, pos = _load_percent(arg, pos)
            ret += enc
            # no unquoted atom contains a percent
            raw = None
            continue
        elif char == "+":
            ret += " "
            if raw is not None:
                raw += "+"
            pos += 1
            continue
        elif opts.aqf and char == "!":
            ret += char
            if raw is not None:
                raw += char
            pos += 1
            if pos < len(arg):
                char = arg[pos]
                if char in "(),:!":
                    ret += char
                    if raw is not None:
                        raw += char
                    pos += 1
        elif _is_unencoded(char) or char == "'":
            ret += char
            if raw is not None:
                raw += char
            pos += 1
        else:
            if len(ret) == 0:
                raise ParseError(f"Unexpected empty value at pos {pos}")
            return _convert_unquoted_atom(raw, ret, opts), pos


def _load_list_data(arg: str, pos: int, opts: LoadOpts) -> list:
    """Parse a list. pos points after the first item"""
    ret: List[Any] = []
    if pos == len(arg):
        return ret
    while True:
        item, pos = _load_any(arg, pos, opts)
        ret.append(item)
        if pos == len(arg):
            return ret
        char = arg[pos]
        if char == ",":
            pos += 1
            continue
        raise ParseError(f"Unexpected char {char!r} at pos {pos} in list")


def _load_list(
    arg: str, pos: int, first_element: Any, opts: LoadOpts
) -> Tuple[list, int]:
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
            item, pos = _load_any(arg, pos, opts)
            ret.append(item)
            continue
        raise ParseError(f"Unexpected char {char!r} at pos {pos} in list")


def _load_dict(arg: str, pos: int, first_key: Any, opts: LoadOpts) -> Tuple[dict, int]:
    first_val, pos = _load_any(arg, pos, opts)
    ret = {first_key: first_val}
    while True:
        if pos == len(arg):
            raise ParseError(f"Unterminated dict")
        char = arg[pos]
        if char == ")":
            return ret, pos + 1
        if char == ",":
            pos += 1
        key, pos = _load_atom(arg, pos, opts)
        if pos == len(arg):
            raise ParseError(f"Unterminated dict, missing value")
        char = arg[pos]
        if char != ":":
            raise ParseError(f"Unexpected char {char!r} at pos {pos}, expected :")
        pos += 1
        val, pos = _load_any(arg, pos, opts)
        ret[key] = val


def _load_comp(arg: str, pos: int, opts: LoadOpts) -> Tuple[Any, int]:
    """Parse a composite: list or dict"""
    val, pos = _load_atom(arg, pos, opts)
    if pos == len(arg):
        raise ParseError("Unterminated composite")
    char = arg[pos]
    if char == ":":
        pos += 1
        return _load_dict(arg, pos, val, opts)
    if char == ",":
        return _load_list(arg, pos, val, opts)
    if char == ")":
        return _load_list(arg, pos, val, opts)
    raise ParseError(f"Unexpected char {char} at pos {pos}, expected , or :")


def _load_any(arg: str, pos: int, opts: LoadOpts) -> Tuple[Any, int]:
    if pos == len(arg):
        raise ParseError(f"Unexpected end of input")
    if arg[pos] == "(":
        pos += 1
        if pos == len(arg):
            raise ParseError("Unterminated composite, expected value")
        char = arg[pos]
        if char == "(":
            first_val, pos = _load_any(arg, pos, opts)
            return _load_list(arg, pos, first_val, opts)
        if opts.distinguish_empty_list_dict and char == ":":
            pos += 1
            if pos == len(arg):
                raise ParseError("Unterminated empty composite, expected )")
            char = arg[pos]
            if char == ")":
                return {}, pos + 1
            else:
                raise ParseError("Unterminated empty composite, expected )")
        if char == ")":
            if opts.distinguish_empty_list_dict:
                return [], pos + 1
            else:
                return {}, pos + 1
        return _load_comp(arg, pos, opts)
    else:
        return _load_atom(arg, pos, opts)


def _load_top(arg: str, pos: int, opts: LoadOpts) -> Any:
    ret, pos = _load_any(arg, pos, opts)
    if pos != len(arg):
        char = arg[pos]
        raise ParseError(f"Expected end of input at {pos}, got {char!r}")
    return ret


def _load_dict_data(arg: str, pos: int, opts: LoadOpts) -> dict:
    ret: Dict[str, Any] = {}
    if pos == len(arg):
        return ret
    while True:
        key, pos = _load_atom(arg, pos, opts)
        if pos == len(arg):
            raise ParseError(f"Unterminated dict, missing value")
        char = arg[pos]
        if char != ":":
            raise ParseError(f"Unexpected char {char!r} at pos {pos}, expected :")
        pos += 1
        val, pos = _load_any(arg, pos, opts)
        ret[key] = val
        if pos == len(arg):
            return ret
        char = arg[pos]
        if char != ",":
            raise ParseError(
                f"Unexpected char {char!r} at pos {pos}, expected , or end of input"
            )
        pos += 1


@overload
def loads(arg: str, opts: Optional[LoadOpts] = None) -> Any:
    ...


@overload
def loads(
    arg: str,
    *,
    implied_dict: bool = False,
    implied_list: bool = False,
    aqf: bool = False,
    distinguish_empty_list_dict: bool = False,
) -> Any:
    ...


def loads(arg: str, opts=None, **kw) -> Any:
    """
    Convert a json object into a jsonurl string

    Options can be passed as a `LoadOpts` object or as individual keyword arguments.
    """
    if opts is None:
        opts = LoadOpts(**kw)
    elif kw:
        raise ValueError("Either opts or kw, not both")

    if opts.aqf:
        arg = _partial_decode_aqf(arg)
    if opts.implied_dict:
        return _load_dict_data(arg, 0, opts)
    if opts.implied_list:
        return _load_list_data(arg, 0, opts)
    return _load_top(arg, 0, opts)


def _add_common_args(parser):
    parser.add_argument(
        "-l",
        "--implied-list",
        action="store_true",
        help="Implied Array mode",
    )
    parser.add_argument(
        "-d",
        "--implied-dict",
        action="store_true",
        help="Implied Object mode",
    )
    parser.add_argument(
        "-a",
        "--address-query-friendly",
        dest="aqf",
        action="store_true",
        help="Address Bar Query String Friendly mode",
    )


def create_parser():
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__, prog="jsonurl-py")
    subtop = parser.add_subparsers(dest="subcmd", metavar="SUBCMD", required=True)

    sub = subtop.add_parser("load", help="Parse JSONURL input and output JSON")
    _add_common_args(sub)
    sub.add_argument("--indent", type=int, help="Output indent spaces per level")

    sub = subtop.add_parser("dump", help="Parse JSON input and output JSONURL")
    _add_common_args(sub)

    return parser


def main(argv=None):
    import json

    common_keys = ["implied_list", "implied_dict", "aqf"]
    opts = create_parser().parse_args(argv)
    if opts.subcmd == "load":
        load_opts = LoadOpts(**{k: getattr(opts, k) for k in common_keys})
        input = sys.stdin.read().rstrip("\n")
        data = loads(input, load_opts)
        sys.stdout.write(json.dumps(data, indent=opts.indent) + "\n")
    elif opts.subcmd == "dump":
        dump_opts = DumpOpts(**{k: getattr(opts, k) for k in common_keys})
        input = sys.stdin.read()
        data = json.loads(input)
        sys.stdout.write(dumps(data, dump_opts) + "\n")
    else:  # pragma: no cover
        raise ValueError(f"Unhandled subcmd {opts.subcmd}")


if __name__ == "__main__":
    main()

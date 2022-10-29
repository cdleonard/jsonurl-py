import json
import string

import pytest

import jsonurl_py as jsonurl
from conftest import (
    assert_load,
    assert_load_fail,
    assert_roundtrip,
    assert_roundtrip_data,
)


def test_dumps():
    assert jsonurl.dumps(dict(a=1)) == "(a:1)"
    assert jsonurl.dumps(dict(a="b c")) == "(a:b+c)"
    assert jsonurl.dumps(dict(a="b$c")) == "(a:b%24c)"


def test_dump_empty_string():
    assert "''" == jsonurl.dumps("")
    assert "(a:'')" == jsonurl.dumps(dict(a=""))


def test_percent_caps():
    assert_load("ll", "%6c%6C")
    assert_load("jklmno", r"%6A%6B%6C%6D%6E%6F")


def test_percent_error():
    assert_load_fail(r"%6")
    assert_load_fail(r"%6c%")
    assert_load_fail(r"%6c%6")


def test_dump_escape_aqf():
    assert "a!!" == jsonurl.dumps("a!", aqf=True)


def test_dump_escape_nonaqf():
    assert "a%21" == jsonurl.dumps("a!", aqf=False)


def test_dump_null_aqf():
    assert "!null" == jsonurl.dumps("null", aqf=True)


def test_load_null_aqf():
    assert "null" == jsonurl.loads("!null", aqf=True)


def test_aqf_escape_once():
    assert_load(["!", ""], "!!,!e", aqf=True, implied_list=True)
    assert_load(["!", ""], "(!!,!e)", aqf=True, implied_list=False)
    assert_load([",", ")"], "!,,!)", aqf=True, implied_list=True)


def test_roundtrip_aqf_escapes():
    assert_roundtrip("a!!", "a!", aqf=True)
    assert_roundtrip("!!", "!", aqf=True)


def test_roundtrip_aqf_escape_paren():
    assert_roundtrip("!(", "(", aqf=True)


def test_roundtrip_aqf_structural():
    assert_roundtrip_data(
        ["!", "+", "(", ")", ",", ":"],
        aqf=True,
        implied_list=True,
    )


def test_roundtrip_aqf_escape_many():
    assert_roundtrip_data(
        ["!", "a!", "!a", "!e", "e!", "!(", "", None, True, "true"],
        aqf=True,
        implied_list=True,
    )


def test_dump_empty_string_aqf():
    assert_roundtrip("(!e:a)", {"": "a"}, aqf=True)
    assert_roundtrip("(a:!e)", {"a": ""}, aqf=True)
    assert_roundtrip("!e:a", {"": "a"}, aqf=True, implied_dict=True)
    assert_roundtrip("a:!e", {"a": ""}, aqf=True, implied_dict=True)


def test_dump_numlike_string():
    assert "(a:'123')" == jsonurl.dumps(dict(a="123"))
    assert "(a:'1e3')" == jsonurl.dumps(dict(a="1e3"))
    assert "(a:'1e-3')" == jsonurl.dumps(dict(a="1e-3"))
    assert "(a:%2B123)" == jsonurl.dumps(dict(a="+123"))


def test_percent():
    jsonurl._load_percent("%31", 0)[0] == chr(0x11)
    jsonurl._load_percent("%41%42", 0)[0] == chr(0x41) + chr(0x42)


def test_loads_atoms():
    assert jsonurl.loads("aaa") == "aaa"
    assert jsonurl.loads("123") == 123
    assert jsonurl.loads("true") == True
    assert jsonurl.loads("false") == False
    assert jsonurl.loads("null") == None


def test_loads_dict():
    assert jsonurl.loads("(a:b)") == dict(a="b")
    assert jsonurl.loads("(a:1)") == dict(a=1)


def test_loads_dict_many():
    assert jsonurl.loads("(a:1,b:2,c:3)") == dict(a=1, b=2, c=3)


def test_loads_list():
    assert jsonurl.loads("(a,b)") == ["a", "b"]
    assert jsonurl.loads("(true,false,1,null)") == [True, False, 1, None]
    assert jsonurl.loads("(a,(1,2),b)") == ["a", [1, 2], "b"]


def test_empty_input():
    with pytest.raises(jsonurl.ParseError):
        jsonurl.loads("")


def test_unenc():
    assert "a~/*b" == jsonurl.loads("a~/*b")


def test_empty_composite():
    assert {} == jsonurl.loads("()")


def test_one_item_list():
    assert [1] == jsonurl.loads("(1)")


def test_one_item_nested_list():
    assert [[1]] == jsonurl.loads("((1))")


def test_number():
    assert 1.2 == jsonurl.loads("1.2")
    assert -1e3 == jsonurl.loads("-1e3")
    assert 3.2e-5 == jsonurl.loads("3.2e-5")
    assert 3.2e5 == jsonurl.loads("3.2e+5")


def test_dumps_float():
    assert "1.2" == jsonurl.dumps(1.2)
    assert "1000.0" == jsonurl.dumps(1e3)
    assert "1000.0" == json.dumps(1e3)


def test_error_on_plus_number():
    with pytest.raises(Exception):
        json.loads("+123")
    assert jsonurl.loads("+123") == " 123"


def test_nonumber():
    assert "1" == jsonurl.loads("%31")


def test_qstr():
    assert "abc" == jsonurl.loads("'abc'")


def test_load_quote_percent():
    assert "'" == jsonurl.loads(r"%27")
    assert "''" == jsonurl.loads(r"%27%27")
    assert "'true'" == jsonurl.loads(r"%27true%27")


def test_save_implied_list():
    assert "a,'1'" == jsonurl.dumps(["a", "1"], implied_list=True)


def test_load_implied_list():
    assert ["a", "b"] == jsonurl.loads("a,b", implied_list=True)
    assert ["a", {"b": "c"}] == jsonurl.loads("a,(b:c)", implied_list=True)
    with pytest.raises(jsonurl.ParseError):
        jsonurl.loads("a,b:c,", implied_list=True)
    with pytest.raises(jsonurl.ParseError):
        jsonurl.loads("a,,", implied_list=True)


def test_save_implied_dict():
    assert "a:'1',b:''" == jsonurl.dumps(dict(a="1", b=""), implied_dict=True)


def test_load_implied_dict():
    assert dict(a="1", b="") == jsonurl.loads("a:'1',b:''", implied_dict=True)


def test_empty_implied_list_save():
    assert "" == jsonurl.dumps([], implied_list=True)


def test_empty_implied_dict_save():
    assert "" == jsonurl.dumps({}, implied_dict=True)


def test_empty_implied_list_load():
    assert [] == jsonurl.loads("", implied_list=True)


def test_empty_implied_dict_load():
    assert {} == jsonurl.loads("", implied_dict=True)


def test_unquote_aqf():
    assert "true" == jsonurl._unquote_aqf("true")
    assert "true" == jsonurl._unquote_aqf("!true")
    assert "1e23" == jsonurl._unquote_aqf("1e!23")
    with pytest.raises(jsonurl.ParseError):
        jsonurl._unquote_aqf("1!e23")
    assert "1e-23" == jsonurl._unquote_aqf("1e!-23")
    assert "1e+23" == jsonurl._unquote_aqf("1e!+23")
    assert "hi!ho?" == jsonurl._unquote_aqf("hi!!ho?")
    with pytest.raises(jsonurl.ParseError):
        jsonurl._unquote_aqf("hi!ho?")


def test_bool_percent():
    assert True == jsonurl.loads("true", aqf=False)
    assert True == jsonurl.loads("true", aqf=True)
    assert "true" == jsonurl.loads("%74rue", aqf=False)
    assert "true" == jsonurl.loads("%74rue", aqf=True)
    assert "!true" == jsonurl.loads("%21%74rue", aqf=False)
    assert "!true" == jsonurl.loads("!%74rue", aqf=False)
    assert "!true" == jsonurl.loads("%21true", aqf=False)
    assert "!true" == jsonurl.loads("!true", aqf=False)
    assert "true" == jsonurl.loads("%21%74rue", aqf=True)
    assert "true" == jsonurl.loads("!%74rue", aqf=True)
    assert "true" == jsonurl.loads("%21true", aqf=True)
    assert "true" == jsonurl.loads("!true", aqf=True)


def test_more_aqf():
    assert_load("", "!e", aqf=True)
    assert_load("true", "!true", aqf=True)
    assert_load("n", "!n", aqf=True)
    assert_load("n", "%21n", aqf=True)
    assert_load("n", "!%6e", aqf=True)
    assert_load(")", "!)", aqf=True)
    assert_load("true", "%74rue", aqf=True)
    assert_load("!true", "!!true", aqf=True)
    assert_load("false", "!false", aqf=True)
    assert_load(True, "true", aqf=True)
    assert_load(False, "false", aqf=True)
    assert_load("hi!", "hi!!", aqf=True)
    assert_load("hi)", "hi!)", aqf=True)


def test_structural_aqf():
    assert_load("(", "!(", aqf=True)
    assert_load("(", "!%28", aqf=True)
    assert_load("(", "%21(", aqf=True)
    assert_load("(", "%21%28", aqf=True)
    with pytest.raises(jsonurl.ParseError):
        jsonurl.loads("%28%21", aqf=True)
    assert_load("(!", "%28%21", aqf=False)
    assert_load("(", "%21(", aqf=True)
    assert_load("z(", "%7a%21%28", aqf=True)


def test_unterminated_qstr():
    assert_load_fail("'ab")
    assert_load_fail("a,'ab", implied_list=True)


def test_percent_qstr():
    assert_load("a'b", "a%27b")
    assert_load("a'b", "'a%27b'")
    assert_load("abc", "'ab%63'")
    assert_load_fail("'ab%6'")
    assert_load_fail("'ab%'")


def test_aqf_escape_after_percent():
    assert_load("true", "%74rue", aqf=True)
    assert_load("trun", "%74ru!n", aqf=True)


def test_aqf_e_invalid_escape():
    assert_load_fail("a!eb", aqf=True)
    assert_load_fail("a!e", aqf=True)
    assert_load_fail("!ea", aqf=True)


def test_plus_in_qstr():
    assert_load("a b", "'a+b'")


def test_space_in_qstr():
    assert_load_fail("'a b'")


def test_unterminated_dict():
    assert_load_fail("(a:b,")
    assert_load_fail("(a:b,c")
    assert_load_fail("(a:b,c:")
    assert_load_fail("(a:b,c:d")


def test_unterminated_dict_implied():
    assert_load_fail("a:b,", implied_dict=True)
    assert_load_fail("a:b,c", implied_dict=True)
    assert_load_fail("a:b,c:", implied_dict=True)
    assert_load_fail("a:b,c,", implied_dict=True)
    assert_load_fail("a:b,c:d:", implied_dict=True)


def test_unencoded_ascii_digits():
    text = string.ascii_letters + string.digits
    assert text == jsonurl.dumps(text)
    assert text == jsonurl.loads(text)


def test_load_unencoded_special():
    text = "-._~!$*/;?@"
    assert text == jsonurl.loads(text)


def test_dump_unencoded_special():
    assert "%21%24%2A%2F%3B%3F%40" == jsonurl.dumps("!$*/;?@")
    assert "-._~" == jsonurl.dumps("-._~")
    assert "%24%2A%2F%3B%3F%40" == jsonurl.dumps("$*/;?@", aqf=True)
    assert "%24%2A%2F%3B%3F%40%27" == jsonurl.dumps("$*/;?@'", aqf=True)


def test_aqf_single_quote_safe():
    assert "a%27b" == jsonurl.dumps("a'b", aqf=True)
    assert "a'b" == jsonurl.dumps("a'b", safe="'", aqf=True)
    assert "a'b" == jsonurl.loads("a'b", aqf=True)


def test_noaqf_single_quote_safe():
    with pytest.raises(ValueError):
        jsonurl.dumps("a'b", safe="'")
    assert "a%27b" == jsonurl.dumps("a'b", aqf=False)


def test_bad_safe():
    with pytest.raises(ValueError):
        jsonurl.dumps("a^b", safe="^")
    with pytest.raises(jsonurl.ParseError):
        jsonurl.loads("a^b")


def test_fail_load_brackets():
    for char in r"[](){}":
        assert_load_fail(char)


def test_dict_with_list_as_first_value():
    assert_load({"a": [1, 2]}, "(a:(1,2))")


def test_nested_list():
    assert_load([[1, 2], 3], "((1,2),3)")
    assert_load([1, [2, 3]], "(1,(2,3))")


def test_aqf_escape_colon():
    assert_load(":", "!:", aqf=True)


def test_aqf_escape_semicolon():
    assert_load_fail("!;", aqf=True)


def test_aqf_load_apos():
    assert_load("'ab", "'ab", aqf=True)
    assert_load("a'b", "a'b", aqf=True)
    assert_load("ab'", "ab'", aqf=True)


def test_notaqf_load_apos_mid_fail():
    assert_load_fail("'ab", aqf=False)
    assert_load("a'b", "a'b", aqf=False)
    assert_load("ab'", "ab'", aqf=False)


def test_dump_badvalue():
    import datetime

    d = datetime.datetime.now()
    with pytest.raises(TypeError):
        json.dumps(dict(d=d))
    with pytest.raises(TypeError):
        jsonurl.dumps(dict(d=d))


def test_badargs():
    with pytest.raises(ValueError):
        jsonurl.dumps("aaa", jsonurl.LoadOpts(), aqf=True)  # type: ignore
    with pytest.raises(ValueError):
        jsonurl.loads("aaa", jsonurl.LoadOpts(), aqf=True)  # type: ignore


def test_aqf_percent_structural():
    assert_load(["a", "b"], r"%28a%2cb%29", aqf=True)
    assert_load({"a": "b"}, r"%28a%3ab%29", aqf=True)


def test_aqf_ampersand():
    assert_load("a&b", r"a%26b", aqf=True)
    assert_load_fail(r"a&b", aqf=True)
    assert_load("a=b", r"a%3db", aqf=True)
    assert_load_fail(r"a=b", aqf=True)


def test_unterminated_percent_message():
    with pytest.raises(jsonurl.ParseError, match="Unterminated percent at pos 2"):
        jsonurl.loads("ab%a")
    with pytest.raises(jsonurl.ParseError, match="Unterminated percent at pos 1"):
        jsonurl.loads("a%a", aqf=True)


def test_invalid_bang_escape_message():
    with pytest.raises(jsonurl.ParseError, match="Invalid !-escaped char 0x61"):
        jsonurl.loads("!a", aqf=True)


ERROR_STRINGS = [
    "(",
    ")",
    "{",
    "}",
    ",",
    ":",
    "(1",
    "(1,",
    "(a:",
    "(a:b",
    "1,",
    "()a",
    "(1)a",
    "(|",
    "((1)",
    "(1(",
    "((1,2,)",
    "(1,1",
    "(1,a,()",
    "(((1,1(",
    "(((1))",
    "((a:b)",
    "(a:b,'')",
    "((a:b(",
    "(a:b,c)",
    "(a:b,c:)",
    "(a:b,c:,)",
    "(a&b)",
    "(a=b)",
    "'a=b'",
    "'a&b'",
    "(a:)",
    "(:a)",
    "(a,,c)",
]


@pytest.mark.parametrize("arg", ERROR_STRINGS)
def test_errors_strings(arg: str):
    with pytest.raises(jsonurl.ParseError):
        jsonurl.loads(arg)


PARSE_DATA = [
    ["()", {}],
    [
        "(true:true,false:false,null:null,empty:(),single:(0),nested:((1)),many:(-1,2.0,3e1,4e-2,5e0))",
        {
            True: True,
            False: False,
            None: None,
            "empty": {},
            "single": [0],
            "nested": [[1]],
            "many": [-1, 2.0, 3e1, 4e-2, 5],
        },
    ],
    ["(1)", [1]],
    ["(1,(2))", [1, [2]]],
    ["(1,(a:2),3)", [1, {"a": 2}, 3]],
    [
        "(age:64,name:(first:Fred))",
        {
            "age": 64,
            "name": {"first": "Fred"},
        },
    ],
    ["(null,null)", [None, None]],
    ["(a:b,c:d,e:f)", {"a": "b", "c": "d", "e": "f"}],
    ["Bob's+house", "Bob's house"],
    ["(%26true)", ["&true"]],
    ["((%26true))", [["&true"]]],
]


@pytest.mark.parametrize("arg_out", PARSE_DATA)
def test_parse_data(arg_out):
    arg, out = arg_out
    assert jsonurl.loads(arg) == out


def test_dump_safe():
    assert jsonurl.dumps("a'b", aqf=True) == "a%27b"
    assert jsonurl.dumps("a^b", aqf=True) == "a%5Eb"
    assert jsonurl.dumps("a/b", aqf=True) == "a%2Fb"
    assert jsonurl.dumps("a@b", aqf=True) == "a%40b"
    assert jsonurl.dumps("a/b", aqf=True, safe="/@") == "a/b"
    assert jsonurl.dumps("a@b", aqf=True, safe="@/") == "a@b"
    assert jsonurl.dumps("a/b", aqf=False, safe="/@") == "a/b"
    assert jsonurl.dumps("a@b", aqf=False, safe="@/") == "a@b"
    assert jsonurl.dumps("a-b", aqf=True) == "a-b"
    assert jsonurl.dumps("a}{b", aqf=True) == "a%7D%7Bb"
    assert jsonurl.dumps("a,b", aqf=True) == "a!,b"


def test_distinguish_empty():
    assert jsonurl.loads("(:)", distinguish_empty_list_dict=True) == {}
    assert jsonurl.loads("()", distinguish_empty_list_dict=True) == []
    assert jsonurl.loads("()", distinguish_empty_list_dict=False) == {}
    with pytest.raises(jsonurl.ParseError):
        assert jsonurl.loads("(:)", distinguish_empty_list_dict=False)


def test_distinguish_error():
    assert_load_fail("a:(:x)", distinguish_empty_list_dict=True, implied_dict=True)
    assert_load_fail("a:(:", distinguish_empty_list_dict=True, implied_dict=True)
    assert_load_fail("a:(", distinguish_empty_list_dict=True, implied_dict=True)
    assert_load_fail("a:(x", distinguish_empty_list_dict=True, implied_dict=True)


def test_distinguish_empty_complex():
    assert_roundtrip(
        "a:(:),b:(),c:null",
        dict(a={}, b=[], c=None),
        distinguish_empty_list_dict=True,
        implied_dict=True,
    )

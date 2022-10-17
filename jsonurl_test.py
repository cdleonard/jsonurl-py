import json

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
    assert "true" == jsonurl.unquote_aqf("true")
    assert "true" == jsonurl.unquote_aqf("!true")
    assert "1e23" == jsonurl.unquote_aqf("1e!23")
    assert "1e23" == jsonurl.unquote_aqf("1!e23")
    assert "1e-23" == jsonurl.unquote_aqf("1e!-23")
    assert "1e+23" == jsonurl.unquote_aqf("1e!+23")
    assert "hi!ho?" == jsonurl.unquote_aqf("hi!!ho?")
    with pytest.raises(jsonurl.ParseError):
        jsonurl.unquote_aqf("hi!ho?")


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

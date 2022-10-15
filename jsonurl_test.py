import pytest
import jsonurl


def test_dumps():
    assert jsonurl.dumps(dict(a=1)) == "(a:1)"
    assert jsonurl.dumps(dict(a="b c")) == "(a:b+c)"
    assert jsonurl.dumps(dict(a="b$c")) == "(a:b%24c)"


def test_percent():
    jsonurl._parse_percent("%31", 0)[0] == chr(0x11)
    jsonurl._parse_percent("%41%42", 0)[0] == chr(0x41) + chr(0x42)


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

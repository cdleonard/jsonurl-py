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

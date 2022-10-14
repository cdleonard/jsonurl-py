import jsonurl


def test_dumps():
    assert jsonurl.dumps(dict(a=1)) == "(a:1)"
    assert jsonurl.dumps(dict(a="b c")) == "(a:b+c)"
    assert jsonurl.dumps(dict(a="b$c")) == "(a:b%24c)"

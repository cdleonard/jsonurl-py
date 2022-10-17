import pytest

import jsonurl_py as jsonurl


def assert_load(data, text, **kw):
    data_load = jsonurl.loads(text, **kw)
    assert data_load == data


def assert_load_fail(text, **kw):
    with pytest.raises(jsonurl.ParseError):
        jsonurl.loads(text, **kw)


def assert_roundtrip(text, data, **kw):
    text_dump = jsonurl.dumps(data, **kw)
    data_load = jsonurl.loads(text, **kw)
    assert text_dump == text and data_load == data


def assert_roundtrip_data(data, **kw):
    text_dump = jsonurl.dumps(data, **kw)
    data_load = jsonurl.loads(text_dump, **kw)
    assert data_load == data

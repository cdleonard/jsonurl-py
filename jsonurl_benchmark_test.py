import pytest

pytest.importorskip("pytest_benchmark")
import jsonurl_py as jsonurl
from conftest import assert_roundtrip_data

BENCHMARK_DATA = {
    "a": 1,
    "b": [1, 2, 3, 4, 5, 6],
    "aaa": "Aaa",
    "abc": "ddd",
    "": "null",
    "exc": ["!", "a!", "!a", "!e", "e!", "!("],
    "t": True,
    "f": False,
    "n": None,
    "f": -1.2445,
    "many": ["aaa", "bbb", "ccc", "ddd", "eee"],
    "abc": {
        "xxx": 123,
        "yyy": [3, 6, 7],
        "zzz": 1e3,
    },
}


def test_roundtrip_aqf():
    assert_roundtrip_data(BENCHMARK_DATA, aqf=True)
    assert_roundtrip_data(BENCHMARK_DATA, aqf=True, implied_dict=True)


def test_loads(benchmark):
    text = jsonurl.dumps(BENCHMARK_DATA)
    data = benchmark(lambda: jsonurl.loads(text))
    assert data == BENCHMARK_DATA


def test_dumps(benchmark):
    text = benchmark(lambda: jsonurl.dumps(BENCHMARK_DATA))
    assert jsonurl.loads(text) == BENCHMARK_DATA

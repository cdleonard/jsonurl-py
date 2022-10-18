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


@pytest.mark.parametrize("aqf", [True, False])
def test_loads(benchmark, aqf: bool):
    text = jsonurl.dumps(BENCHMARK_DATA, aqf=aqf)
    data = benchmark(lambda: jsonurl.loads(text, aqf=aqf))
    assert data == BENCHMARK_DATA


@pytest.mark.parametrize("aqf", [True, False])
def test_dumps(benchmark, aqf: bool):
    text = benchmark(lambda: jsonurl.dumps(BENCHMARK_DATA, aqf=aqf))
    data = jsonurl.loads(text, aqf=aqf)
    assert data == BENCHMARK_DATA

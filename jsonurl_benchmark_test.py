import pytest

pytest.importorskip("pytest_benchmark")
import jsonurl_py as jsonurl
from conftest import assert_roundtrip_data

BENCHMARK_DATA = {
    "a": 1,
    "digits": [1, 2, 3, 4, 5, 6],
    "aaa": "aaa",
    "odd strings": [
        " spa ce ",
        "'quo'te'",
        "&amper&sand&",
        "^car^et^",
        "+pl+us+",
        "#ha#sh#",
        "=eq=ual=",
        "/sl/ash/",
        "\\back\\slash\\",
        "$dol$lar$",
        ":co:lon:",
        ",com,ma,",
        "(par)(en)",
        ")par)en(",
    ],
    "": "empty-key",
    "empty-val": "",
    "exc": ["!", "e!", "!e", "!(", "!)", "a!b"],
    "structural": [",", "(", ")", ":"],
    "t": True,
    "f": False,
    "n": None,
    "tstr": "true",
    "fstr": "false",
    "nstr": "null",
    "float": -1.2445,
    "nest": [
        None,
        False,
        True,
        "text",
        12,
        3.4,
        [
            None,
            False,
            True,
            "text",
            12,
            3.4,
            ["a", "b"],
            {"a": "b"},
        ],
        {
            "null": None,
            "false": False,
            "true": True,
            "text": "with space",
            "one two": 12,
            "three,four": 3.4,
            "list": ["a", 1],
            "dict": {"a": 1},
        },
    ],
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

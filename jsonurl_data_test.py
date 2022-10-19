"""
Run tests from https://github.com/cdleonard/jsonurl-test-data
"""
import json
from pathlib import Path

import pytest

import jsonurl_py as jsonurl

data_path = Path(__file__).parent / "test-data/test_data.json"
if not data_path.exists():
    pytest.skip("Test data not found", allow_module_level=True)

with data_path.open("r") as f:
    JSON_TEST_DATA = json.load(f)


def _param_values():
    return [name for name in JSON_TEST_DATA if name != "$schema"]


@pytest.mark.parametrize("name", _param_values())
def test(name: str):
    global JSON_TEST_DATA
    item = JSON_TEST_DATA[name]
    type = item.get("type", "roundtrip")
    kw = {}
    val = item.get("implied_array")
    if val is not None:
        kw["implied_list"] = val
    val = item.get("implied_object")
    if val is not None:
        kw["implied_dict"] = val
    val = item.get("aqf")
    if val is not None:
        kw["aqf"] = val
    if type == "roundtrip":
        text = item["text"]
        data = item["data"]
        assert jsonurl.loads(text, **kw) == data and jsonurl.dumps(data, **kw) == text
    elif type == "load":
        text = item["text"]
        data = item["data"]
        assert jsonurl.loads(text, **kw) == data
    elif type == "fail":
        text = item["text"]
        with pytest.raises(jsonurl.ParseError):
            jsonurl.loads(text, **kw)
    else:
        raise ValueError("unknown data item type={type!r}")

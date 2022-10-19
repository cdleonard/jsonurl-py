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


@pytest.mark.parametrize("index", range(len(JSON_TEST_DATA)))
def test(index: int):
    global JSON_TEST_DATA
    item = JSON_TEST_DATA[index]
    type = item.get("type", "roundtrip")
    if type == "roundtrip":
        text = item["text"]
        data = item["data"]
        assert jsonurl.loads(text) == data and jsonurl.dumps(data) == text
    elif type == "fail":
        text = item["text"]
        with pytest.raises(jsonurl.ParseError):
            jsonurl.loads(text)
    else:
        raise ValueError("unknown data item type={type!r}")
import pytest

import jsonurl_py as jsonurl

# From https://www.kermitproject.org/utf8.html
lines = [
    "我能吞下玻璃而不伤身体",
    "أنا قادر على أكل الزجاج و هذا لا يؤلمني",
    "Я могу есть стекло, оно мне не вредит",
]


@pytest.mark.parametrize("index", range(len(lines)))
def test(index: int):
    text = lines[index]
    dump = jsonurl.dumps(text)
    text_load = jsonurl.loads(dump)
    assert text_load == text

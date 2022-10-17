import subprocess
import sys


def run(
    argv,
    text=True,
    check=True,
    capture_output=True,
    **kw,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "jsonurl_py"] + argv,
        text=text,
        check=check,
        capture_output=True,
        **kw,
    )


def test_main_load():
    proc = run(["load"], input="(a:1)")
    assert proc.stdout == '{"a": 1}\n'


def test_main_load_list():
    proc = run(["load", "--implied-list"], input="a,1")
    assert proc.stdout == '["a", 1]\n'


def test_main_load_dict():
    proc = run(["load", "--implied-dict"], input="a:b")
    assert proc.stdout == '{"a": "b"}\n'


def test_main_load_aqf():
    proc = run(["load", "-a"], input="(a,!1,!true)")
    assert proc.stdout == '["a", "1", "true"]\n'


def test_main_dump():
    proc = run(["dump"], input='{"a":1}')
    assert proc.stdout == "(a:1)\n"


def test_main_dump_list():
    proc = run(["dump", "--implied-list"], input='["a", 1]')
    assert proc.stdout == "a,1\n"


def test_main_dump_dict():
    proc = run(["dump", "--implied-dict"], input='{"a":"b"}')
    assert proc.stdout == "a:b\n"


def test_main_dump_aqf():
    proc = run(["dump", "-a"], input='["a", "1", "true"]')
    assert proc.stdout == "(a,!1,!true)\n"

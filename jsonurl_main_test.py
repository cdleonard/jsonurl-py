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


def test_main_dump():
    proc = run(["dump"], input='{"a":1}')
    assert proc.stdout == "(a:1)\n"

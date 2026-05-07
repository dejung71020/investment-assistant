# tests/test_hello.py

import pytest

from core.hello import hello

def test_hello_basic():
    assert hello("이대중") == "Hello, 이대중! 개인 투자 비서가 실행됩니다."

def test_hello_empty_name_raises():
    with pytest.raises(ValueError, match="이름은 비어있을 수 없습니다."):
        hello("")
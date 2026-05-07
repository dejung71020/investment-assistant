# core/hello.py
"""
M0.1 sanity check: a function that proves the project is set up.
MO.1 정상동작 확인: 프로젝트 설정이 완료되었음을 증명하는 함수
"""


def hello(name: str) -> str:
    """
    Return a greeting. Used as the first test case to verify the toolchain.
    인사말을 반환합니다. 도구 모음(Toolchain)이 잘 작동하는지 확인하는 첫 번째 테스트 케이스로 사용합니다.
    """
    if not name:
        raise ValueError("이름은 비어있을 수 없습니다.")
    return f"Hello, {name}! 개인 투자 비서가 실행됩니다."
# investment-assistant
Personal investment analyst assistant - daily stock scoring (KOSPI200 + S&amp;P 500)

# Investment Assistant

개인 투자 분석 비서 — KOSPI200 + S&P500 일일 종목 점수 시스템.

## 상태
M0.1 진행 중 (프로젝트 골격 완료, GCP 셋업 전)

## 모드
분석가 비서 — 점수와 분석만 제공, 매매는 본인이 직접 실행.

## 스택
- Backend: Python 3.10+, GCP (Cloud Run, Firestore, Pub/Sub)
- LLM: Gemini API (런타임)
- Frontend: Flutter (예정)

## 개발

```bash
python -m venv .venv
.venv\\Scripts\\activate    # Windows
pip install -e \".[dev]\"
pytest
```

## 문서
- 시스템 설계: `docs/design_v2.md`
- 운영 매뉴얼: `docs/MANUAL.md`

## 라이선스
MIT
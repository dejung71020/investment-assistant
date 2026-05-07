# 개인 투자 분석 비서 — 프로젝트 운영 매뉴얼

**이 문서의 위치**: NotebookLM "v2 Project Hub" 노트북에 적재되는 단일 진실 자료. 새 Claude/Gemini 대화 시작 시 첫 메시지에 이 문서의 "§1 30초 요약"만 붙여 넣으면 됩니다.

**작성**: 이대중 / **작성일**: 2026-05-07 / **버전**: v2.1

---

## 목차

1. [30초 요약 (대화 시작용)](#1-30초-요약-대화-시작용)  
2. [프로젝트 핵심 결정사항](#2-프로젝트-핵심-결정사항)  
3. [3-도구 워크플로우](#3-3-도구-워크플로우)  
4. [GitHub 사용 가이드 (처음 한 번 자세히)](#4-github-사용-가이드-처음-한-번-자세히)  
5. [브랜치 전략과 Phase 매핑](#5-브랜치-전략과-phase-매핑)  
6. [일상 Git 명령어 치트시트](#6-일상-git-명령어-치트시트)  
7. [NotebookLM 적재 자료 목록](#7-notebooklm-적재-자료-목록)  
8. [일일 작업 루틴](#8-일일-작업-루틴)  
9. [체크리스트 모음](#9-체크리스트-모음)  
10. [자주 막히는 순간과 대응](#10-자주-막히는-순간과-대응)

---

## 1\. 30초 요약 (대화 시작용)

이 블록을 새 Claude/Gemini 대화에 그대로 붙여 넣으세요.

프로젝트: 개인 투자 분석 비서 (이대중 본인용, single-user)

모드: 분석가 비서 (자동매매 X, 점수·분석만 제공)

스택: GCP \+ Gemini API \+ Python \+ Flutter

예산: 월 USD 20 이하

종목: KOSPI200 \+ S\&P500 약 700종목, 일 1회 장 마감 후 평가

점수: 0\~100 float, L1(원자지표 20개) → L2(5카테고리) → L3(최종)

안전: Hard Filter 5종(PER 100↑, PSR 30↑, 적자+성장둔화, 부채위험, EPS 4Q하향) \+ Veto Gate 3종

보유 목표: 8종목 집중, KIS API 조회전용으로 동기화

LLM 분담: 차트 비전·뉴스·정성보정·리포팅은 Gemini API, 매매결정은 코드만

파이프라인: 700 → Hard Filter → L1·L2 → 상위50+보유8 LLM → L3+Veto

참고: v2 설계서, V1 투자철학 문서 모두 NotebookLM에 있음

---

## 2\. 프로젝트 핵심 결정사항

이 표는 "왜 이렇게 정했지?"를 잊지 않기 위한 것. 새 결정이 나오면 여기 추가.

| 결정 | 내용 | 이유 |
| :---- | :---- | :---- |
| 자동매매 폐기 | 점수·분석만 제공 | 자본시장법 리스크, 운영 부담 |
| 단일 사용자 | 멀티테넌트 안 함 | 인증·격리·법적 부담 회피 |
| 친구 공유 방식 | 저장소 fork 후 셀프호스팅 | 본인 인프라에서 타인 자산 X |
| GCP 선택 | AWS 대신 | Gemini와 같은 생태계, 인증 깔끔 |
| LangGraph 미사용 | 단순 함수 체인 | 분기·휴먼인루프 없으므로 과잉 설계 |
| 종목별 점수 | 매크로 비중 조정 X | 직관적 의사결정, 종목 단위 평가 |
| Hard Filter 5종 | Forward PER 100, PSR 30, 적자+성장둔화, 부채+이자보상, EPS 4Q 하향 | 꿈만 믿는 비싼 종목·재무위험 입구컷 |
| KIS 조회전용 | 주문 권한 토큰 발급 X | 자동매매 부재 시 보안 이점 극대화 |
| Flutter | iOS·Android·Web 단일 코드 | "어디서든" 요구 충족 |
| 모노레포 | 5개 서비스 한 저장소 | 단일 사용자에 가장 단순 |
| 저장소 public | 친구 fork 가능 | 단, 시크릿은 절대 커밋 X |

**미해결 결정사항**은 v2 설계서 13장 참조.

---

## 3\. 3-도구 워크플로우

### 3.1 도구별 역할 (한 줄 요약)

| 도구 | 한 줄 역할 |
| :---- | :---- |
| **Claude (웹)** | 설계 결정, 핵심 로직 코드, 디버깅 — 긴 추론 필요한 일 |
| **Gemini Pro (웹)** | 교차검증 상대, 한국어 작문, 멀티모달 검증 |
| **Gemini API (런타임)** | 시스템 안에서 실제 호출되는 LLM (차트·뉴스·리포트) |
| **NotebookLM** | 자료 기반 Q\&A, 환각 없는 참조, 프로젝트 메모리 |
| **VS Code** | 코드 작성·Git 조작 통합 환경 |

### 3.2 교차검증 패턴

| 패턴 | 사용 시점 | 방법 |
| :---- | :---- | :---- |
| **Diff Mode** | 설계 결정, 알고리즘 선택 | 같은 질문을 양쪽에 → 답 비교 |
| **Review Mode** | 코드 리뷰 (가장 효율적) | 한쪽이 만들고 → 다른 쪽이 익명으로 검토 |
| **Adversarial Mode** | 중요 분기점, 백테스트 검증 | A의 답을 B에 부딪히기 |

### 3.3 토큰 절약 7대 전략 (Claude 사용량)

1. **세션 단위로 끊기** — 한 주제 끝나면 새 대화, 이전 인계 문서를 첫 메시지로  
2. **NotebookLM에 프로젝트 메모리** — Claude한테 컨텍스트 다시 줄 필요 없음  
3. **작업별 도구 분리** — 보일러플레이트는 Gemini 무료, 핵심 로직만 Claude Pro  
4. **첨부 대신 요약** — PDF 매번 첨부 X, 한 번 요약받아 그 텍스트만  
5. **코드 검토는 diff로** — 전체 파일 X, 변경 부분만  
6. **긴 산출물은 한 방에** — 결정 다 모은 뒤 한 번 요청  
7. **Phase별 토큰 집중** — P2(L1 지표)와 P8(백테스트)에 집중 투자

### 3.4 함정 5가지 (피하기)

- 같은 답 받고 안심 → 둘 다 같은 실수 가능, NotebookLM이 최종 권위  
- 의견 다르니 절충 → 보통 둘 중 하나가 맞음, "왜 다른지" 캐묻기  
- 무한 검토 루프 → "양쪽 검증 1회로 끝" 종료 조건 명시  
- 컨텍스트 비대칭 → Gemini한테는 30초 요약 또는 v2 설계서 첨부  
- 합의 편향 → 다른 쪽에 보일 때 "누가 만들었다" 익명화

---

## 4\. GitHub 사용 가이드 (처음 한 번 자세히)

Git을 처음 쓰시는 분 기준으로 한 번만 자세히. 이 섹션이 끝나면 §6 치트시트를 보고 일하시면 됩니다.

### 4.1 핵심 개념 (5분 이해)

- **Repository(저장소·repo)**: 프로젝트 폴더 하나 \+ 변경 이력  
- **Commit(커밋)**: 변경사항을 "이 시점"으로 저장하는 행위. 일종의 스냅샷  
- **Branch(브랜치)**: 평행 우주처럼 여러 작업을 분리. `main`이 정식 라인  
- **Push/Pull**: 내 PC ↔ GitHub 서버 동기화 (push는 올리기, pull은 받기)  
- **Merge(병합)**: 다른 브랜치의 변경사항을 현재 브랜치로 합치기  
- **Pull Request (PR)**: 브랜치를 main에 합치기 전 "이렇게 합치자" 제안 (혼자 써도 가치 있음 — 변경 이력 정리)

### 4.2 1회성 초기 설정 (Windows)

#### Git 설치 확인

git \--version

나오면 OK. 없으면 [git-scm.com](https://git-scm.com/download/win) 에서 설치.

#### 본인 정보 등록 (한 번만)

git config \--global user.name \\"이대중\\"

git config \--global user.email \\"본인-github-이메일@example.com\\"

git config \--global init.defaultBranch main

git config \--global core.autocrlf true

git config \--global pull.rebase false

#### GitHub 인증 (Personal Access Token)

1. github.com → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token  
2. 권한: `repo` 전체 체크  
3. 만료일: 90일 또는 1년  
4. 생성된 토큰 복사 → **잃어버리면 다시 만들어야 함, 비밀번호 매니저에 저장**  
5. VS Code에서 push 시도하면 사용자명·암호 묻는데 암호 자리에 토큰 붙여넣기

### 4.3 저장소 만들기

#### 1\. GitHub 웹에서 저장소 생성

1. github.com 로그인 → 우측 상단 `+` → New repository  
2. 저장소명: `investment-assistant` (또는 본인 선호)  
3. **Public** 선택 (친구 공유 대비)  
4. "Add a README file" 체크  
5. ".gitignore" template: **Python**  
6. License: MIT (간단하고 친구 fork에 친화적)  
7. Create repository

#### 2\. 로컬에 클론 (PowerShell 또는 Git Bash)

cd C:\\Users\\본인이름\\Documents

git clone https://github.com/본인-github-id/investment-assistant.git

cd investment-assistant

#### 3\. VS Code로 열기

code .

(`.`은 현재 폴더)

### 4.4 첫 커밋 만들기 (VS Code에서)

1. VS Code 왼쪽 사이드바 "Source Control" 아이콘 (가지 모양) 클릭  
2. README.md를 수정하거나 새 파일 추가  
3. 변경된 파일이 "Changes" 목록에 나타남  
4. 파일 옆 `+` 버튼 → "Staged Changes"로 이동 (커밋할 항목 선택)  
5. 위쪽 메시지 박스에 커밋 메시지 입력 (예: `chore: initial project structure`)  
6. ✓ Commit 버튼  
7. "Sync Changes" 버튼 (또는 ↑ Push) → GitHub에 반영

**팁**: 커밋 메시지 컨벤션 (이대중님 프로젝트에서 사용)

- `feat:` 새 기능 (예: `feat: add RSI calculator`)  
- `fix:` 버그 수정 (예: `fix: handle division by zero in PER`)  
- `refactor:` 동작 그대로, 코드 정리  
- `test:` 테스트 추가/수정  
- `docs:` 문서 변경  
- `chore:` 빌드·설정 변경

### 4.5 .gitignore 필수 추가 항목

GitHub가 만들어준 Python `.gitignore`에 다음을 **반드시 추가**:

\# 시크릿 (절대 커밋 금지\!)

.env

.env.\*

\*.key

\*.pem

service-account-\*.json

secrets/

\# 로컬 데이터

data/raw/

data/processed/

\*.parquet

\*.csv

\# IDE

.vscode/settings.json  \# 본인 설정만, 공유하려면 제외

.idea/

\# 빌드 결과물

dist/

build/

\*.egg-info/

\# Flutter

\*\*/.dart\_tool/

\*\*/build/

**시크릿이 한 번이라도 커밋되면 영원히 이력에 남습니다.** Public 저장소라 즉시 노출됩니다. 항상 커밋 전에 "내가 이 파일에 토큰·키 넣었나?" 점검.

만약 실수로 시크릿을 커밋했다면 → 그 자리에서 *해당 키를 무효화하고 새로 발급*. 이력 청소는 어렵고 의미 없음.

---

## 5\. 브랜치 전략과 Phase 매핑

### 5.1 브랜치 종류 (단일 사용자에 맞춘 단순화)

main                      ← 항상 동작하는 코드. 절대 깨지면 안 됨

 ├── develop (선택)        ← 통합 개발 라인 (단일 사용자면 생략 가능)

 ├── feat/p2-rsi-score    ← Phase 2의 RSI 지표 작업

 ├── feat/p4-llm-prompt   ← Phase 4의 LLM 프롬프트 작업

 ├── fix/per-zero-bug     ← 버그 수정

 └── docs/update-readme   ← 문서만 수정

**단일 사용자 프로젝트에서는 `develop` 브랜치 생략을 추천**합니다. `main`이 단순히 "마지막으로 동작 확인된 상태"이고, feature 브랜치에서 작업 → main으로 PR. 끝.

### 5.2 브랜치 명명 규칙

`<타입>/<phase>-<짧은-설명>`

- 타입: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`  
- phase: `p0`\~`p9` 또는 생략 가능  
- 설명: 영어 소문자, 하이픈 구분, 짧게

**예시**:

- `feat/p1-yfinance-collector`  
- `feat/p2-dupont-roe`  
- `feat/p2-chart-pattern-llm`  
- `fix/p2-loss-company-per`  
- `refactor/p3-l2-weights-config`  
- `docs/update-manual`

### 5.3 Phase별 브랜치 전략

| Phase | 권장 브랜치 패턴 | 이유 |
| :---- | :---- | :---- |
| **P0 인프라** | `chore/p0-*` 1\~2개 | Terraform, GitHub Actions 등 |
| **P1 데이터 수집** | `feat/p1-<api>-collector` 데이터 소스별로 분리 | KIS·yfinance·FRED·DART 각각 |
| **P2 L1 지표** ⭐ | **지표 1개당 1개 브랜치** (총 \~20개) | 함수+테스트가 한 PR로 끝나는 단위. 교차검증도 한 브랜치 단위로 |
| **P3 L2·L3·Veto** | `feat/p3-l2-aggregator`, `feat/p3-veto-gate` 2\~3개 | 합성 로직, 거부권 |
| **P4 LLM Analyzer** | `feat/p4-prompt-tuning`, `feat/p4-vision-chart` | Gemini 연동·프롬프트 |
| **P5 Reporter** | `feat/p5-*` 1\~2개 | 한국어 리포트 |
| **P6 Flutter** | **화면 1개당 1개 브랜치** | 대시보드, 종목 상세 등 |
| **P7 KIS 연동** | `feat/p7-kis-balance` | 보유 종목 동기화 |
| **P8 백테스트** | `feat/p8-vectorbt-engine`, `feat/p8-shadow-portfolio` | 적대적 검증 비중 큼 |

⭐ **P2가 핵심**: 지표 함수 하나가 잘못되면 전체 점수가 무너집니다. 1지표 \= 1브랜치 \= 1PR로 가서 *각 지표가 독립적으로 검증된 후 main에 합류*.

### 5.4 표준 작업 흐름 (한 기능을 끝내기까지)

1\. main에서 시작

   git switch main

   git pull

2\. 새 브랜치 만들기

   git switch \-c feat/p2-dupont-roe

3\. 작업 (코드 \+ 테스트)

   ... 파일 편집 ...

4\. 커밋 (자주, 작게)

   VS Code Source Control → Stage → Commit → Push

5\. GitHub에서 PR 생성

   브랜치 push 후 \\"Compare & pull request\\" 버튼

6\. 본인이 리뷰 (혼자 PR이라도 가치 있음 — diff 한눈에)

   \- Files changed 탭에서 변경사항 점검

   \- 테스트 통과 확인 (GitHub Actions)

   \- Claude/Gemini 교차검증 (선택)

7\. Merge

   \\"Squash and merge\\" 추천 (작은 커밋 1개로 합쳐 main 이력 깔끔)

8\. 로컬 정리

   git switch main

   git pull

   git branch \-d feat/p2-dupont-roe

### 5.5 PR 템플릿 (지표 작업용)

`.github/PULL_REQUEST_TEMPLATE.md` 파일로 저장하면 PR 만들 때 자동 채워짐:

\#\# 무엇을

\[ \] 새 지표 추가: \<지표명\>

\[ \] 기존 지표 수정

\[ \] 버그 수정

\[ \] 리팩터링

\#\# 변경 내용

\- 함수: \`core/indicators/\<파일\>.py\`의 \`\<함수명\>\`

\- 입력 정의: ...

\- 출력 0\~100 정규화 방식: ...

\#\# 테스트

\- \[ \] 단위 테스트 (알려진 종목 골든 케이스)

\- \[ \] 경계값 테스트 (적자, 신규 상장, 분모 0\)

\- \[ \] 횡단면 검증 (같은 산업 종목 분포 합리적)

\#\# 교차검증

\- \[ \] Claude 검토

\- \[ \] Gemini 검토

\- \[ \] NotebookLM 공식 자료 대조

\#\# 메모

(여기에 시간 절약 팁이나 막혔던 점)

---

## 6\. 일상 Git 명령어 치트시트

이대중님이 VS Code Git 탭을 주로 쓰실 거라 GUI 동작 위주, CLI는 막힐 때 폴백.

### 6.1 매일 쓰는 것 (VS Code 기준)

| 하고 싶은 것 | VS Code | CLI |
| :---- | :---- | :---- |
| 변경사항 확인 | Source Control 아이콘 | `git status` |
| 파일 staging | 파일 옆 `+` | `git add <파일>` |
| 모두 staging | Changes 옆 `+` | `git add .` |
| 커밋 | 메시지 입력 → ✓ Commit | `git commit -m \"메시지\"` |
| Push | Sync Changes 버튼 | `git push` |
| Pull | ... 메뉴 → Pull | `git pull` |
| 브랜치 전환 | 좌하단 브랜치명 클릭 | `git switch <브랜치>` |
| 새 브랜치 | 좌하단 → "Create new branch" | `git switch -c <새이름>` |

### 6.2 가끔 쓰는 것 (CLI 권장)

\# 마지막 커밋 메시지 수정 (push 전에만\!)

git commit \--amend \-m \\"새 메시지\\"

\# 마지막 커밋 취소 (변경 내용은 유지)

git reset \--soft HEAD\~1

\# 변경사항 임시 저장 (브랜치 전환해야 할 때)

git stash

git stash pop  \# 다시 꺼내기

\# 특정 파일을 직전 커밋 상태로 되돌리기

git checkout HEAD \-- \<파일\>

\# 브랜치 목록

git branch \-a

\# 원격 브랜치 가져오기

git fetch

git pull

\# 로컬 브랜치 삭제 (병합 완료 후)

git branch \-d \<브랜치명\>

\# 강제 삭제 (병합 안 했어도)

git branch \-D \<브랜치명\>

\# 원격 브랜치 삭제

git push origin \--delete \<브랜치명\>

### 6.3 응급 상황 (실수했을 때)

\# 잘못된 브랜치에서 작업 중이라면

git stash

git switch \<올바른브랜치\>

git stash pop

\# 커밋했는데 잘못된 브랜치라면

git log \--oneline \-3        \# 커밋 해시 확인

git reset \--hard HEAD\~1     \# 현재 브랜치에서 마지막 커밋 제거 (변경도 사라짐\!)

git switch \<올바른브랜치\>

git cherry-pick \<해시\>      \# 그 커밋만 가져오기

\# Push했는데 시크릿이 들어갔다면

1\. 즉시 해당 키 무효화 (Gemini API, KIS, GitHub Token 등)

2\. 새 키 발급

3\. 코드에서 시크릿 제거 \+ .env로 이동 \+ 커밋

4\. 이력 청소는 시도하지 말 것 (복잡하고 의미 없음, 키만 새로 발급하면 됨)

---

## 7\. NotebookLM 적재 자료 목록

### 7.1 노트북 3개 구성

#### Notebook A: "v2 Project Hub" (이대중님이 가장 자주 쓸 것)

| 자료 | 형식 | 비고 |
| :---- | :---- | :---- |
| 본 운영 매뉴얼 (이 파일) | Markdown | 단일 진실 자료 |
| v2 설계서 | DOCX 또는 PDF | 시스템 설계 |
| V1 투자 철학 문서 | PDF | 원본 의도 |
| 기능 리스트 46개 | TXT | V1 함께 받은 것 |
| 결정 히스토리 | Markdown | 새 결정 추가될 때 갱신 |
| 인계 문서 (대화 끝마다 갱신) | Markdown | 다음 대화 시작용 요약 |

#### Notebook B: "API References" (구현 중 막힐 때)

| 자료 | 출처 |
| :---- | :---- |
| KIS Open API 문서 | apiportal.koreainvestment.com 다운로드 |
| FRED API 가이드 | fred.stlouisfed.org/docs/api |
| yfinance README | github.com/ranaroussi/yfinance |
| DART OpenAPI 매뉴얼 | opendart.fss.or.kr |
| Finnhub API 문서 | finnhub.io/docs/api |
| Pub/Sub 핵심 개념 | cloud.google.com/pubsub |
| Cloud Run 배포 가이드 | cloud.google.com/run/docs |
| Firestore 데이터 모델링 | cloud.google.com/firestore/docs |
| Gemini API 문서 | ai.google.dev/gemini-api/docs |
| Flutter Firebase 통합 | firebase.flutter.dev |

#### Notebook C: "Investment Knowledge" (P2 L1 지표 \+ P8 백테스트)

| 자료 | 비고 |
| :---- | :---- |
| 듀폰 분해 정의 | Investopedia 문서 |
| RSI·MACD·이동평균 정의 | 신뢰할 만한 출처 (Investopedia, 한국거래소) |
| vectorbt 튜토리얼 | 공식 문서 |
| 백테스트 함정 (look-ahead bias 등) | 학술 자료 |
| 한국 양도소득세 가이드 | 국세청 |
| 미국 주식 세금 가이드 | 본인 적용 사항만 |

### 7.2 적재 시 주의사항

- **저작권**: 책 전체 PDF는 지양, 공식 문서·블로그 글 위주  
- **버전**: API 문서는 버전 표기 (예: "KIS API 2025-09 버전")  
- **갱신 주기**: 분기 1회 점검, 폐기된 자료 제거  
- **민감 정보**: 본인 잔고·계좌번호·실제 매매 기록은 **절대 NotebookLM에 넣지 말 것** (학습 가능성)

### 7.3 NotebookLM 활용 패턴

- 코드 짜다 막히면 "KIS 잔고 조회 API 응답 형식이 어떻게 돼?" → Notebook B  
- 지표 정의가 헷갈리면 "Sortino ratio 정확한 공식이 뭐야?" → Notebook C  
- 새 대화에서 컨텍스트 필요하면 "v2 설계서 핵심 5줄 요약해줘" → Notebook A  
- 저작권 안전: NotebookLM 답변은 출처 인용이라 안전, 다만 *코드에 그대로 복붙은 금지*

---

## 8\. 일일 작업 루틴

### 8.1 작업 시작 (10분)

1. **VS Code 열기** → 프로젝트 폴더  
2. **main 동기화**: 좌하단 main 클릭 → Pull  
3. **오늘 할 작업 정의** (5분 안에)  
   - Phase가 뭐고, 어떤 지표/화면/기능인지  
   - 1시간 단위로 끝낼 수 있는 단위인지 확인 (아니면 더 쪼개기)  
4. **새 브랜치 생성**: `feat/p<n>-<짧은이름>` 패턴  
5. **인계 문서 또는 컨텍스트 준비**: Claude/Gemini 새 대화 시작 시 §1 30초 요약 \+ 이번 작업 한 줄 설명

### 8.2 작업 중 (집중)

1. **15\~30분 집중 → 작은 커밋** 반복  
   - 큰 변경 한 번보다 작은 변경 여러 번  
   - 커밋 메시지는 `feat: add VIX score normalization` 처럼 구체적  
2. **막히면 NotebookLM 먼저** → 안 풀리면 Claude/Gemini  
3. **교차검증은 "중요한 결정"에서만**  
   - 지표 정확성 (P2): 양쪽 다 검증  
   - 보일러플레이트: 한쪽만, 또는 무료 모델  
4. **시크릿 점검**: 매 커밋 전 `.env`나 키가 staged 영역에 없는지 VS Code에서 한 번 보기

### 8.3 작업 종료 (10분)

1. **현재 브랜치 push**  
2. **PR 생성** (또는 다음날에 이어할 거면 Draft PR)  
3. **인계 메모 갱신**: 오늘 한 것·내일 할 것 1\~2줄을 운영 매뉴얼 §10 하단이나 별도 `JOURNAL.md`에 기록  
4. **결정 히스토리 갱신** (새 결정이 있었다면)  
5. **VS Code 닫기**

### 8.4 주간 루틴 (금요일 권장)

- main 브랜치 안정성 확인 (모든 테스트 통과)  
- 비용 대시보드 점검 (GCP Billing, Gemini API)  
- 미해결 결정사항(v2 설계서 13장) 점검 — 결정 가능한 것 결정  
- NotebookLM 자료 갱신 (새 추가, 폐기 자료 제거)  
- 한 주 회고 1\~2줄 (`JOURNAL.md`)

---

## 9\. 체크리스트 모음

### 9.1 P2 지표 PR 체크리스트

- [ ] 함수가 입력→출력 명확 (Pydantic 타입)  
- [ ] 0\~100 float로 정규화됨  
- [ ] 단위 테스트 (알려진 종목 골든 케이스 ≥ 2개)  
- [ ] 경계값 테스트 (적자, 분모 0, 신규 상장)  
- [ ] 횡단면 합리성 (같은 산업 분포 확인)  
- [ ] Claude 검토 1회  
- [ ] Gemini 검토 1회 (익명화)  
- [ ] NotebookLM에서 정의 재확인  
- [ ] PR 설명 명확  
- [ ] main 머지 후 로컬 브랜치 삭제

### 9.2 시크릿 안전 체크리스트 (매 커밋 전)

- [ ] `.env` 파일이 staged에 없음  
- [ ] 코드에 `\"sk-...\"`, `\"AIza...\"` 같은 키 문자열 없음  
- [ ] `service-account-*.json` 파일 없음  
- [ ] 한국 증권사 토큰 같은 문자열 없음  
- [ ] 본인 잔고·계좌번호 노출 없음

### 9.3 비용 점검 체크리스트 (주 1회)

- [ ] GCP Billing 대시보드: 월 누적 \< $20  
- [ ] Cloud Run 호출 수 (예상치 ±20% 이내)  
- [ ] Gemini API 사용량 (월 예상 1.7K 호출)  
- [ ] Firestore 읽기/쓰기 무료 한도 내  
- [ ] Cloud Storage 사용량 \< 10GB  
- [ ] Budget Alert 설정 동작 확인

### 9.4 새 Phase 시작 체크리스트

- [ ] v2 설계서에서 해당 Phase 산출물 재확인  
- [ ] 미해결 결정사항 (13장) 중 이 Phase 진입 전 결정할 것 처리  
- [ ] NotebookLM에 필요한 자료 적재  
- [ ] 브랜치 명명 규칙 확인  
- [ ] 첫 작업 단위 정의 (1\~3시간 분량)

---

## 10\. 자주 막히는 순간과 대응

### "Claude 토큰이 부족할 것 같다"

→ §3.3 토큰 절약 7대 전략. 특히 *세션 끊기*와 *NotebookLM 메모리화*가 효과 큼.

### "Claude와 Gemini가 다른 답을 줬다"

→ §3.4. 합치지 말고, *왜 다른지* 양쪽에 캐묻기. NotebookLM 공식 자료가 최종 권위.

### "Git에서 뭔가 꼬였다"

→ §6.3 응급 상황. 대부분 `git stash` \+ 브랜치 전환 \+ `stash pop`으로 풀림. 안 풀리면 새 브랜치 만들고 거기서 작업 이어가기 (망친 브랜치는 나중에 정리).

### "시크릿을 실수로 커밋했다"

→ §4.5 끝부분. *키 무효화 \+ 새 발급*이 정답. 이력 청소 시도 X.

### "PR이 너무 커졌다"

→ 작업이 1시간 안에 안 끝났다는 신호. 일단 push해서 Draft PR로 두고, *다음 작업은 새 브랜치*로 분리. 큰 PR은 본인 검토도 어려움.

### "NotebookLM에 무슨 자료를 넣어야 할지 모르겠다"

→ "내가 매번 검색하는 자료"가 답. Claude/Gemini한테 같은 질문을 두 번 하고 있다면 그게 NotebookLM 후보.

### "Phase 진행이 늦어진다"

→ 16주는 빡빡. v2 설계서 7.2 우선순위 줄이기 전략 참조. 차트 패턴 LLM 비전, 횡단면 자동 검증 등은 \*v2.5 (운영 6개월 후)\*로 미뤄도 무방.

### "비용이 예상을 초과했다"

→ 1순위: Gemini API 호출 수. Cloud Run min-instance도 점검. Budget Alert 100% 도달 시 자동 셧다운 동작 확인.

### "새 대화 시작인데 이전 작업이 뭐였는지 까먹었다"

→ §1 30초 요약 \+ `JOURNAL.md` 마지막 줄 \+ NotebookLM "v2 Project Hub".

---

## 부록: 이 매뉴얼 자체의 갱신 룰

- **언제 갱신**: 새 결정 발생 시, Phase 시작/종료 시, 도구 사용 패턴 바뀔 때  
- **어디 갱신**: GitHub 저장소 `docs/MANUAL.md`로 commit  
- **NotebookLM 재적재**: 분기 1회 또는 큰 갱신 시  
- **버전 표기**: 상단 `v2.1` 부분 갱신 (의미 있는 변경마다 \+0.1)

---

**마지막 한마디**: 이 매뉴얼은 "미래의 본인"에게 보내는 편지입니다. 한 달 후 "이거 어떻게 했더라" 하는 순간에 펼쳐서 5분 안에 답이 나오는 게 목표. 답이 안 나오면 그 부분을 보강해서 다시 commit.  

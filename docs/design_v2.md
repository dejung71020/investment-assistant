**개인 투자 분석 비서**

시스템 설계서 v2.0

*종목별 0\~100 점수 기반 다관점 평가 시스템*

작성: 이대중

v1 작성: 매크로 기반 자동 매매 (폐기)

v2 작성: 종목별 점수 기반 분석 비서

# **목차**

# **1\. 개요**

## **1.1 v1과의 차이**

v1은 매크로 기반 자동 매매 시스템이었다. 이대중과의 협의 결과, 다음 두 가지 핵심 변화로 v2를 새로 작성한다.

* **관점 변화:** 시장 매크로 → 종목별 점수. 의사결정의 단위가 "시장 국면"이 아니라 "이 종목 몇 점인가"가 된다.

* **역할 변화:** 자동 매매 폐기. 시스템은 점수와 분석만 제공하고, 매수·매도는 본인이 증권사 앱에서 직접 실행한다 (분석가 비서 모드).

## **1.2 시스템 성격 — 분석가 비서**

이 시스템은 매일 장 마감 후 KOSPI200 \+ S\&P500 약 700종목을 평가하여, 점수·근거·인사이트를 본인에게 제공한다. 주문 실행 책임은 본인에게 있다. 시스템이 잘못된 점수를 보여줘도 본인이 거를 수 있고, 자본시장법·전자금융거래법 리스크가 사실상 사라진다.

## **1.3 핵심 요구사항**

| 항목 | 결정사항 |
| ----- | ----- |
| 사용자 | 이대중 단일 사용자 (single-tenant) |
| 접근성 | iOS·Android·Web (Flutter 단일 코드베이스) |
| 월 예산 | USD 20 이하 |
| 기술 스택 | GCP, Gemini API, Python, Flutter |
| 종목 범위 | KOSPI200 \+ S\&P500, 약 700종목 (중복 제외) |
| 평가 빈도 | 일 1회 (한국·미국 시장 마감 후) |
| 목표 보유 종목 | 8종목 집중 투자 |
| 증권사 연동 | 국내·해외 모두 조회전용 (주문 권한 없음) |
| 점수 형식 | 0.0 \~ 100.0 float |
| 자동 매매 | 없음 (분석·점수만 제공) |
| LLM 활용 | 차트 비전, 뉴스 센티먼트, 정성 보정, 리포팅 |

## **1.4 비목적**

* 주문 실행 (자동 매매 일체 없음)

* 타인 자산 운용 (single-user 절대 사수)

* 실시간 시세 모니터링 (장 마감 후 일 1회 평가만)

* LangGraph 기반 멀티 에이전트 (단순 파이프라인으로 충분)

* LLM에 의한 매매 결정 (LLM은 입력·설명에만 사용)

# **2\. 점수 시스템 설계**

이 시스템의 본체는 종목 평가 점수다. 모든 화면, 모든 알림, 모든 의사결정의 기준이 0\~100 float 점수로 통일된다.

## **2.1 3계층 구조**

| 계층 | 설명 | 개수 | 담당 |
| ----- | ----- | ----- | ----- |
| L1 — Atomic Indicators | 원자 지표. 각 0\~100 | 약 20개 | 코드 \+ LLM |
| L2 — Category Scores | 5개 차원으로 묶인 점수 | 5개 | 코드 |
| L3 — Composite Score | 최종 종합 점수 \+ Veto | 1개 | 코드 \+ LLM 보정 |

## **2.2 L1 — Atomic Indicators**

각 지표는 raw 값을 0\~100 float으로 정규화한 결과다. 정규화 방법은 지표마다 다르다 (z-score → sigmoid, 백분위수, 임계값 매핑 등).

### **2.2.1 Macro Fit (4개 지표)**

* interest\_rate\_fit: 현재 금리 환경에서 이 종목의 적합도 (성장주 vs 가치주 vs 배당주에 따라 다름)

* oil\_sensitivity\_fit: 유가 변화에 대한 종목 민감도 (수혜·중립·피해)

* usd\_strength\_fit: 달러 강세·약세 환경 적합도 (수출·수입 비중에 따라)

* sector\_macro\_alignment: 섹터 전체의 매크로 정렬도 (FRED 매크로 데이터 \+ 섹터 ETF 상대강도)

### **2.2.2 Fundamental (6개 지표)**

* dupont\_roe\_quality: 듀폰 분해 (순이익률 × 자산회전율 × 레버리지). 레버리지 의존도 높으면 감점

* revenue\_growth\_log: 매출 성장률을 로그스케일로 정규화 (큰 회사의 5% 성장 \= 작은 회사의 30% 성장과 비슷한 가치)

* earnings\_growth\_log: 이익 성장률, 로그스케일

* fcf\_quality: 잉여현금흐름 / 매출 비율

* valuation\_relative: PER·PBR·EV/EBITDA를 산업 중앙값 대비 평가 (z-score 기반)

* balance\_sheet\_health: 부채비율, 유동비율, 이자보상배율 통합

### **2.2.3 Technical (5개 지표)**

* rsi\_score: RSI 14일. 과매도(30 미만)에서 가점, 과매수(70 초과)에서 감점

* macd\_score: MACD 시그널 교차와 히스토그램 방향

* ma\_alignment: 이평선 정배열 점수 (5/20/60/120일)

* log\_price\_position: 로그스케일 가격 채널에서의 현재 위치 (V1 로그스케일 지표 요청 반영)

* volume\_profile: 최근 거래량 대비 평균 거래량 비율

### **2.2.4 Sentiment (3개 지표)**

* news\_sentiment\_llm: 최근 7일 뉴스를 LLM이 요약·평가 (-100 \~ \+100 → 0 \~ 100 매핑)

* analyst\_consensus: 애널리스트 매수의견 비율과 목표주가 변화

* institutional\_flow: 외국인·기관 순매수 추세 (KIS API 또는 13F 변화)

### **2.2.5 Chart Pattern \+ Risk (2개 지표)**

* chart\_pattern\_llm: 60일 차트 이미지 \+ 수치를 LLM 비전에 전달, 패턴 인식 (헤드앤숄더, 컵앤핸들, 삼각수렴 등)

* volatility\_score: 60일 일간 수익률의 표준편차, 베타, 최대낙폭

## **2.3 L2 — Category Scores**

L1의 20개 지표를 5개 카테고리로 가중평균한다. 가중치는 백테스트로 캘리브레이션할 대상이며, 초기값은 다음과 같다.

| 카테고리 | 포함 지표 | 초기 가중치 |
| ----- | ----- | ----- |
| Macro Fit | Macro 4종 | 균등 (각 25%) |
| Fundamental | Fundamental 6종 | ROE 25, 성장 30, 가치 25, 재무건강 20 |
| Technical | Technical 5종 | RSI 20, MACD 20, MA 20, 로그가격 25, 거래량 15 |
| Sentiment | Sentiment 3종 \+ chart\_pattern | 뉴스 35, 컨센 25, 수급 20, 차트 20 |
| Risk | volatility\_score \+ 보조 지표 | 변동성 50, 베타 25, MDD 25 |

각 L2 카테고리도 0\~100 float로 산출된다.

## **2.4 L3 — Composite Score**

최종 점수는 다음 3단계로 산출된다.

### **Step 1: 가중평균 (코드)**

L3\_raw \= 0.20 \* L2\_macro  
       \+ 0.30 \* L2\_fundamental  
       \+ 0.20 \* L2\_technical  
       \+ 0.15 \* L2\_sentiment  
       \+ 0.15 \* L2\_risk\_inverted     \# 위험 점수는 반전  
   
\# 초기값: Fundamental 가중 가장 높음 (장기 보유 철학 반영)

### **Step 2: LLM 정성 보정 (제한적)**

L3\_raw가 70 이상 또는 30 이하인 종목, 그리고 보유 8종목에 대해서만 LLM이 보정한다. 보정 폭은 ±10점으로 제한한다 (LLM이 결정을 뒤집지 못하도록).

system \= '''너는 투자 분석 보조다. 주어진 카테고리 점수와   
원자 지표를 보고, 코드가 놓쳤을 정성적 위험·기회를 ±10점으로 보정한다.   
보정 사유를 100자 이내로 명시하라. 임의로 매매를 추천하지 마라.'''  
   
user \= f'''  
종목: {symbol}, L3\_raw: {raw}, L2 카테고리: {l2\_dict}  
최근 뉴스 요약: {news\_summary}  
차트 패턴: {chart\_pattern}  
보정값과 사유를 JSON으로 응답하라.  
'''  
   
→ {"adjustment": \-3.5, "reason": "매출 성장은 양호하나 ..."}

### **Step 3: Hard Filter \+ Veto Gate (코드)**

아무리 점수가 높아도, 다음 조건에 걸리면 추천 후보에서 강제 제외된다.

Hard Filter (절대 제외 — Universe에서 빠짐):

* Forward PER \> 100 (꿈만 믿는 비싼 종목)

* PSR \> 30 (매출 대비 시총이 비현실적)

* 영업이익 적자 \+ 매출 성장률 \< 10% (성장주 정당화 실패)

* 부채비율 \> 200% AND 이자보상배율 \< 1 (재무 위험)

* 최근 4분기 연속 EPS 추정치 하향 (애널리스트 컨센서스 악화)

Veto Gate (점수는 산출하되 추천 리스트에서 제외):

* 어느 한 L2 카테고리라도 30점 이하

* L2\_risk\_inverted \< 50 (위험 점수가 너무 높음)

* LLM 정성 보정에서 "red\_flag" 플래그 (수동 거부)

## **2.5 점수 산출 결과 객체**

class StockScore(BaseModel):  
    symbol: str  
    timestamp: datetime  
    l1\_indicators: dict\[str, float\]      \# 20개 원자 지표  
    l2\_categories: dict\[str, float\]      \# 5개 카테고리  
    l3\_raw: float                        \# LLM 보정 전  
    l3\_adjustment: float                 \# LLM 보정값 (-10 \~ \+10)  
    l3\_final: float                      \# 최종 점수  
    hard\_filter\_pass: bool  
    veto\_gate\_pass: bool  
    rationale: str                       \# LLM 자연어 설명  
    chart\_pattern: str | None            \# 인식된 패턴  
    news\_summary: str                    \# 최근 뉴스 LLM 요약  
    delta\_from\_yesterday: float          \# 어제 대비 점수 변화

# **3\. 일일 평가 파이프라인**

700종목 전체에 LLM을 돌리면 비용이 폭발하므로 깔때기(funnel) 구조로 설계한다. 코드 1차 필터로 좁힌 뒤 LLM은 상위권과 보유 종목에만 집중한다.

## **3.1 4단계 파이프라인**

| Stage | 처리 대상 | 수단 | 예상 시간 | 비용 |
| ----- | ----- | ----- | ----- | :---: |
| 0\. Universe | KOSPI200 \+ S\&P500 ≈ 700 | DB 조회 | \<1초 | $0 |
| 1\. Hard Filter | 700 → 약 500 | 코드 (재무지표) | 30초 | $0 |
| 2\. Quant Score | 500종목 L1·L2 점수 | 코드 (NumPy 벡터) | 2\~5분 | $0 |
| 3\. LLM 정밀 분석 | 상위 50 \+ 보유 8 \= \~58 | Gemini 2.5 Flash | 5\~10분 | \~$0.15/일 |
| 4\. Veto \+ 최종 점수 | 58종목 L3 산출 | 코드 | 10초 | $0 |

일일 LLM 호출 약 58회 × 30일 \= 월 1,740회. Gemini 2.5 Flash 기준 입력 4K \+ 출력 1K 토큰 가정 시 월 $4\~6 추정. 예산 $20 안에서 충분히 여유.

## **3.2 실행 흐름**

* 23:00 KST — Cloud Scheduler가 한국 시장 마감 후 트리거

* 08:00 KST 다음날 — 미국 시장 마감 후 미국 종목 평가 (서머타임 자동 보정)

* 09:00 KST — 양 시장 결과 통합, 최종 추천 리스트 생성, FCM 푸시

## **3.3 LLM이 받는 입력 (예시)**

Stage 3에서 한 종목당 LLM에 전달되는 정보:

{  
  "symbol": "GOOGL",  
  "l2\_scores": {  
    "macro": 72, "fundamental": 88, "technical": 64,  
    "sentiment": 70, "risk": 55  
  },  
  "key\_indicators": {  
    "forward\_per": 21.4, "roe": 28.1, "revenue\_growth\_yoy": 14.2,  
    "rsi\_14": 58, "macd\_signal": "bullish\_cross\_3d\_ago"  
  },  
  "recent\_news": \[...최근 7일 헤드라인 10개...\],  
  "chart\_image\_b64": "...60일 차트 PNG 이미지...",  
  "chart\_metrics": {  
    "trend": "uptrend", "support": 165, "resistance": 182  
  }  
}

## **3.4 LLM이 반환하는 출력**

{  
  "adjustment": \-2.0,  
  "reason": "펀더멘털과 매크로는 양호하나 RSI 58·MACD 골든크로스 후 "   
             "3일 경과로 단기 조정 가능성. Risk 카테고리 55점 의식.",  
  "chart\_pattern": "ascending\_triangle",  
  "news\_summary": "제미나이 광고 매출 호조, 반독점 소송 진행 중",  
  "red\_flag": false,  
  "watch\_points": \["반독점 판결 D-30", "AI 자본지출 발표"\]  
}

## **3.5 산출물**

매일 09:00 KST에 다음이 Firestore에 저장되고 Flutter 앱에 스트리밍된다.

* 전체 종목의 점수 (L1·L2·L3) — 본인 보유 종목 우선 정렬

* Top 20 추천 (Veto·Hard Filter 통과, L3 점수 내림차순)

* Top Movers (어제 대비 점수 변화 ±5점 이상)

* 보유 8종목 일일 카드 (점수·근거·뉴스 요약·차트 패턴)

* 일일 시장 리포트 (LLM이 위 데이터를 종합한 한국어 요약)

# **4\. 데이터 소스**

## **4.1 시세 데이터**

| 용도 | 소스 | 비용 | 비고 |
| ----- | ----- | :---: | ----- |
| 미국 일봉 | yfinance | 무료 | 비공식, 다운 시 폴백 필요 |
| 미국 일봉 폴백 | Alpaca Markets API | 무료 | 계정 필요, 안정적 |
| 한국 일봉 | KIS Open API | 무료 | 조회 한도 일 20,000건 |
| 한국 일봉 폴백 | pykrx (KRX 공식 데이터) | 무료 | 다운로드 안정적 |
| 거래량·OHLC | 위와 동일 | 무료 |  |

## **4.2 재무·매크로 데이터**

| 용도 | 소스 | 비용 | 비고 |
| ----- | ----- | :---: | ----- |
| 미국 재무제표 | FMP (Financial Modeling Prep) | 무료 250req/일 | 캐싱 필수 |
| 한국 재무제표 | DART OpenAPI | 무료 | 공식 데이터 |
| 애널리스트 컨센서스 | yfinance (info.targetMeanPrice) | 무료 | 한국은 NAVER 비공식 |
| 거시지표 (금리·CPI 등) | FRED API | 무료 | 안정적 |
| 환율 | FRED 또는 ExchangeRate.host | 무료 |  |

## **4.3 뉴스 데이터**

| 용도 | 소스 | 비용 | 비고 |
| ----- | ----- | :---: | ----- |
| 미국 종목 뉴스 | yfinance ticker.news | 무료 | Yahoo Finance 출처 |
| 미국 종목 뉴스 보강 | Finnhub API | 무료 60req/분 | 헤드라인만 |
| 한국 종목 뉴스 | NAVER 뉴스 검색 API | 무료 | 쿼리 종목명 |
| 글로벌 시장 뉴스 | RSS (Reuters, Bloomberg 헤드라인) | 무료 | 전문은 저작권 주의 |

## **4.4 보유 종목 데이터 (조회전용)**

자동 매매를 하지 않으므로, 증권사 API는 보유종목·잔고 조회 권한만 사용한다. 주문 권한 토큰은 발급하지 않는다.

* 국내: 한국투자증권 KIS Open API — 잔고조회 (TR\_ID: TTTC8434R)만 사용

* 해외: 한국투자증권 KIS Open API — 해외주식 잔고조회 (TR\_ID: TTTS3012R) 사용

* KIS 단일 계정으로 국내·미국 모두 가능 → IBKR 별도 연동 불필요

* 토큰 갱신: refresh token으로 자동 갱신 (Cloud Run \+ Secret Manager)

* 폴백: API 다운 시 본인이 Flutter 앱에서 수동 입력 가능

## **4.5 데이터 캐싱 전략**

외부 API 호출량을 줄이기 위해 다층 캐싱:

* 일봉 시세: Cloud Storage에 Parquet으로 영구 저장. 신규 일자만 추가

* 재무제표: Firestore에 분기 단위로 저장. 다음 분기까지 재호출 안 함

* 뉴스: Firestore에 7일 보존, 이후 GCS로 이관

* 매크로 (FRED): Firestore에 일 단위 저장

# **5\. 시스템 아키텍처**

## **5.1 컴포넌트 (자동매매 제거 후 단순화)**

| 계층 | 서비스 | 역할 | GCP 제품 |
| ----- | ----- | ----- | ----- |
| 트리거 | Scheduler | 일일 평가 트리거 | Cloud Scheduler |
| 트리거 | Event Bus | Stage 간 이벤트 전달 | Pub/Sub |
| 컴퓨트 | Data Collector | 시세·재무·뉴스 수집 | Cloud Run |
| 컴퓨트 | Score Engine | L1·L2·Hard Filter·Veto | Cloud Run |
| 컴퓨트 | LLM Analyzer | Stage 3 LLM 정밀 분석 | Cloud Run |
| 컴퓨트 | Reporter | 일일 한국어 리포트 생성 | Cloud Run |
| 컴퓨트 | API Gateway | Flutter 앱용 REST | Cloud Run |
| 저장 | Operational DB | 점수·보유·설정 | Firestore |
| 저장 | Time-series | 시세·재무 히스토리 | Cloud Storage |
| 저장 | Secrets | KIS 토큰·API 키 | Secret Manager |
| 관측 | Logs | 감사 로그·에러 | Cloud Logging |
| 관측 | Budget | 월 $20 예산 알림 | Billing Budget |
| 알림 | Push | 일일 리포트 푸시 | FCM |
| 인증 | Auth | 본인 단일 계정 | Firebase Auth |

v1 대비 Trade Executor 컴포넌트 1개가 제거되었고, 대신 LLM Analyzer가 명시적으로 분리되었다.

## **5.2 데이터 흐름 (Daily Cycle)**

* 23:00 KST — Scheduler가 "daily-eval-kr" Pub/Sub 발행

* Data Collector — KOSPI200 시세·재무·뉴스 수집 → "data-ready-kr" 발행

* Score Engine — Hard Filter → L1·L2 계산 → 상위 50 추출 → "need-llm" 발행

* LLM Analyzer — 상위 50 \+ 보유 8 처리 → "llm-done-kr" 발행

* 06:00 KST — "daily-eval-us" 트리거 → 동일 흐름으로 미국 종목 처리

* 09:00 KST — Reporter가 양 시장 통합 리포트 생성 → Firestore 저장 → FCM 푸시

## **5.3 단순 파이프라인 (LangGraph 미사용)**

v1과 동일하게 그래프 추상화 없이 함수 체인으로 구현한다. 분기·휴먼 인 더 루프가 없으므로 LangGraph 불필요.

\# apps/score\_engine/main.py  
def run\_daily\_eval(market: Literal\['KR','US'\]) \-\> list\[StockScore\]:  
    universe \= load\_universe(market)  
    survived \= \[s for s in universe if pass\_hard\_filter(s)\]  
    snapshots \= collector.batch\_load(survived)  
   
    \# L1·L2 벡터 연산 (NumPy)  
    l1\_df \= compute\_l1\_indicators(snapshots)  
    l2\_df \= aggregate\_to\_l2(l1\_df)  
   
    \# 상위 50 \+ 보유 종목 추출  
    top50 \= l2\_df.nlargest(50, 'l2\_avg').index.tolist()  
    holdings \= firestore\_repo.get\_holdings()  
    targets \= list(set(top50) | set(holdings))  
   
    \# LLM Stage 3  
    llm\_results \= llm\_analyzer.batch\_analyze(targets, l2\_df, snapshots)  
   
    \# L3 \+ Veto  
    scores \= \[\]  
    for sym in universe:  
        s \= build\_stock\_score(sym, l1\_df, l2\_df, llm\_results.get(sym))  
        s.veto\_gate\_pass \= check\_veto(s)  
        scores.append(s)  
   
    firestore\_repo.save\_scores(scores)  
    return scores

# **6\. 지표 검증 ("면밀히 검토" 원칙)**

점수 계산이 틀리면 모든 게 무너진다. 모든 L1 지표 함수는 다음 3가지 테스트를 통과해야 운영에 투입된다.

## **6.1 단위 테스트 (결정론적)**

실제 종목의 알려진 시점 데이터로 골든 케이스를 만들어 둔다. 라이브러리·API 변경으로 결과가 바뀌면 즉시 감지.

\# tests/unit/test\_dupont.py  
def test\_dupont\_aapl\_2024\_q4():  
    fixture \= load\_fixture('AAPL\_2024\_q4')  
    result \= compute\_dupont\_roe\_quality(fixture)  
    assert 95 \<= result \<= 100   \# AAPL은 ROE 매우 우수  
   
def test\_dupont\_loss\_making\_company():  
    fixture \= load\_fixture('LOSS\_CO\_2024\_q4')  
    result \= compute\_dupont\_roe\_quality(fixture)  
    assert result \< 30           \# 적자 기업은 낮아야 함

## **6.2 경계값 테스트**

실패 모드를 의도적으로 만들어 본다.

* 적자 기업의 PER (분모 음수): 점수 0 또는 N/A 처리

* 신규 상장 (60일 미만 데이터): 차트 지표 None, 점수 산출 안 함

* 거래 정지: 거래량·MACD None, 펀더멘털만으로 점수 산출

* 분할·합병 직후: 가격 데이터 보정 적용 확인

## **6.3 횡단면 검증**

같은 산업 종목들의 점수 분포가 합리적인지 확인. 예시:

* S\&P500 빅테크 7종목의 Fundamental 점수 평균이 시장 평균보다 높아야 함

* 적자 바이오테크의 Fundamental 점수가 50 이하 분포에 모여야 함

* 동일 섹터 ETF 구성종목의 Macro Fit 분산이 작아야 함 (같은 거시 영향)

이 테스트는 데이터를 가져오므로 통합 테스트로 분류, 매일 새벽 1회 자동 실행.

## **6.4 시각적 검증 도구**

Flutter 앱에 "Indicator Inspector" 화면 추가. 종목 선택 → L1 20개 지표 raw 값과 0\~100 점수를 모두 보여줌. 점수가 이상해 보이면 즉시 raw 값으로 디버깅 가능.

# **7\. 비용 분석 (월 $20 이내)**

## **7.1 사용량 가정**

* Cloud Run 호출: 일 100회 (4개 서비스 × 25회) \= 월 3,000회

* LLM 호출: 일 58회 × 30일 \= 월 1,740회 (입력 4K \+ 출력 1K 토큰)

* Firestore 읽기: 일 20,000 / 쓰기: 일 2,000

* Cloud Storage: 누적 10GB (시세 \+ 차트 이미지 캐시)

* 외부 API: yfinance·FRED·DART·KIS·Finnhub 모두 무료

## **7.2 비용 추정**

| 항목 | 무료 티어 | 예상 사용 | 월 비용 (USD) |
| ----- | ----- | ----- | ----- |
| Cloud Run | 월 200만 req | 3K req | $0 |
| Cloud Scheduler | 3 job 무료 | 3 job | $0 |
| Pub/Sub | 월 10GB 무료 | \<200MB | $0 |
| Firestore | 1GB·일 50K read·20K write | 여유 있음 | $0 |
| Cloud Storage | 5GB Standard 무료 | 10GB | $0.10 |
| Secret Manager | 월 6 secret 무료 액세스 | 5 secret | $0 |
| Cloud Logging | 월 50GB 무료 | \<2GB | $0 |
| Gemini 2.5 Flash | 유료 (가격 변동 가능) | 월 1.7K호출 | $4\~6 |
| Firebase Auth | 월 50K MAU 무료 | 1 사용자 | $0 |
| FCM | 무료 | 일 5건 | $0 |
| KIS·FRED·yfinance | 무료 | \- | $0 |
| 네트워크 egress | 월 1GB 무료 | \<1GB | $0 |
| 예비비 | \- | \- | $3 |
| **합계** |  |  | **$7\~10** |

예산 $20 한도에서 약 $10\~13의 여유가 있다. 다음 용도로 활용 가능:

* Cloud Run min-instance=1 (cold start 제거, 약 $5\~7 추가)

* Gemini Pro로 업그레이드 (정밀도 향상, 비용 약 5배)

* LLM 호출 빈도 증대 (전 종목 LLM 분석 등)

## **7.3 예산 가드레일**

* GCP Billing Budget: 50%·80%·100% 임계값 알림

* 100% 도달 시 Cloud Function이 모든 Cloud Run을 비활성화

* 일일 비용 트렌드 Looker Studio 무료 대시보드

# **8\. 데이터 모델**

## **8.1 Firestore 컬렉션**

/users/{uid}/                       \# 단일 사용자  
  profile  
   
/users/{uid}/holdings/{symbol}      \# KIS API 동기화  
  symbol, market, quantity, avg\_price, current\_price,  
  market\_value, last\_synced  
   
/users/{uid}/watchlist/{symbol}     \# 관심종목 (수동)  
  symbol, added\_at, note  
   
/scores/{date}/stocks/{symbol}      \# 일자별 점수  
  symbol, l1\_indicators, l2\_categories,  
  l3\_raw, l3\_adjustment, l3\_final,  
  hard\_filter\_pass, veto\_gate\_pass,  
  rationale, chart\_pattern, news\_summary,  
  delta\_from\_yesterday  
   
/reports/{date}                     \# 일일 시장 리포트  
  date, summary\_kr, top\_picks, top\_movers,  
  holdings\_summary, generated\_at  
   
/system/config  
  weights\_l2, hard\_filter\_thresholds,  
  veto\_thresholds, llm\_model\_version  
   
/system/indicator\_versions          \# 지표 함수 버전  
  function\_name, version, deployed\_at

## **8.2 핵심 Pydantic 모델**

StockScore는 2장에서 정의한 그대로. 추가로 다음 두 모델.

class Holding(BaseModel):  
    symbol: str  
    market: Literal\['KR','US'\]  
    quantity: float  
    avg\_price: float  
    current\_price: float  
    market\_value: float  
    last\_synced: datetime  
   
class DailyReport(BaseModel):  
    date: date  
    summary\_kr: str             \# 3\~5문단 한국어 요약  
    top\_picks: list\[str\]        \# L3 점수 상위 10  
    top\_movers: list\[str\]       \# 어제 대비 ±5점  
    holdings\_summary: dict\[str, dict\]  \# 보유 8종목 일일 카드  
    market\_overview: str        \# 양 시장 매크로 한 줄  
    generated\_at: datetime

# **9\. 프론트엔드 (Flutter)**

## **9.1 화면 구성**

| 화면 | 주요 기능 |
| ----- | ----- |
| 대시보드 | 오늘의 시장 한 줄 요약, 보유 8종목 점수 카드, Top Movers |
| 보유 종목 | 8종목 상세, 점수 변화 추이, KIS API 동기화 버튼 |
| 추천 리스트 | Top 20 (L3 점수 내림차순), 종목 클릭 → 상세 |
| 관심종목 | 수동 추가/제거, 점수 추적 |
| 종목 상세 | L1 20개 지표, L2 5개 카테고리, LLM 리포트, 차트, 뉴스 |
| Indicator Inspector | L1 raw 값과 정규화 점수 동시 표시 (디버깅·신뢰성 검증용) |
| 일일 리포트 | 최근 30일 리포트 아카이브, 검색 |
| 과거 추천 추적 | 어제·일주일 전 추천 종목의 실제 수익률 추적 (시스템 신뢰도 검증) |
| 설정 | L2 가중치 조정, Hard Filter 임계값, 알림 ON/OFF, KIS 토큰 |

## **9.2 백엔드 연동**

* 실시간: Firestore Listener (StreamBuilder)

* 커맨드: API Gateway REST (POST /trigger-eval, POST /sync-holdings)

* 인증: Firebase Auth \+ ID Token

* 푸시: FCM (일일 리포트, Top Movers ±10점 이상 변동 시 즉시 알림)

## **9.3 핵심 UI 원칙**

자동 매매가 없으므로 UI가 곧 제품이다. 다음 원칙을 지킨다.

* 점수와 근거를 항상 함께 보여준다 ("왜?"가 즉시 보여야 함)

* 어제 대비 변화를 시각적으로 강조 (색상·화살표)

* LLM 리포트는 펼치기/접기로 짧게·길게 둘 다 지원

* "이 점수 이상하다" 피드백 버튼 → 추후 가중치 튜닝 자료

# **10\. 시스템 신뢰도 검증**

자동 매매가 없으므로 "실제 거래 결과로 검증" 경로가 차단된다. 대신 다음 두 방법으로 시스템을 지속 검증한다.

## **10.1 Shadow Portfolio (가상 포트폴리오)**

매일 시스템이 추천한 Top 20 종목을 가상으로 "매수"한다고 가정하고 성과를 추적한다. 실제 본인 포트폴리오 성과와 비교.

* 매일 점수 70점 이상 신규 진입 종목을 가상 동일가중 매수

* 점수 30점 이하로 떨어지면 가상 매도

* 월간·분기간 누적 성과를 SPY/KOSPI200과 비교

* 샤프비율, 최대낙폭, 승률 등 표준 지표 산출

## **10.2 백테스트**

과거 5\~10년 데이터로 시스템을 시뮬레이션. 단, 자동 매매가 없으므로 "이 시스템 신호를 따랐을 때"의 가상 성과만 평가한다.

* 라이브러리: vectorbt 권장 (고속 벡터 연산)

* 주의: 미래 누설 (look-ahead bias) 방지 — 시점별로 그 당시 알려진 데이터만 사용

* 거래 비용 모델링: 슬리피지 0.1%, 수수료 0.015% (NH/KIS 평균)

* 외환 변동 반영 (해외 종목)

## **10.3 캘리브레이션 대상**

* L2 가중치 5개 (현재: 0.20, 0.30, 0.20, 0.15, 0.15)

* Hard Filter 임계값 (Forward PER 100, PSR 30 등)

* Veto Gate 임계값 (카테고리 30, Risk 50\)

* LLM 보정 한계 (현재: ±10점)

## **10.4 과적합 방지**

* Walk-forward 검증: 2014\~2018 학습 → 2019 검증 → 2015\~2019 학습 → 2020 검증 ...

* Out-of-sample: 최근 1년은 학습에 절대 사용하지 않음

* Sensitivity 분석: 가중치를 ±20% 흔들었을 때 결과가 크게 바뀌면 과적합 의심

# **11\. 보안 및 안전**

## **11.1 자격증명**

* KIS 조회전용 토큰: Secret Manager에 저장. 주문 권한 토큰은 발급하지 않음

* Gemini API 키: Secret Manager

* Firestore 보안 규칙: 본인 UID만 read·write 허용

* Cloud Run 서비스: 전용 서비스 계정, 최소 권한

## **11.2 데이터 프라이버시 (LLM 호출 시)**

Gemini에 전송하는 데이터에서 보유 수량·평균단가·잔고 절대값은 제외한다. LLM은 점수 산출에만 관여하므로 개인 잔고를 알 필요가 없다.

## **11.3 감사 로그**

* 모든 점수 산출 결과 영구 보존 (Firestore \+ GCS)

* LLM 입력·출력 페어 로그 (디버깅·재현용)

* 지표 함수 버전 추적 ("오늘 점수가 어제와 왜 다른가" 추적 가능)

## **11.4 자동 매매 부재의 보안 이점**

자동 매매를 하지 않으므로 다음 위험이 사라진다.

* 주문 토큰 탈취 → 무단 매매 시나리오 (토큰이 조회 권한만 가지므로)

* 야간 알고리즘 폭주 → 자산 손실 (시스템에 매도 권한 자체가 없음)

* 시스템 버그 → 잘못된 주문 (주문 코드 자체가 없음)

# **12\. 구현 로드맵**

| 단계 | 기간 | 산출물 |
| ----- | ----- | ----- |
| P0: 인프라 | 1주 | GCP 프로젝트, Terraform, GitHub repo, CI/CD |
| P1: 데이터 수집 | 2주 | Collector — KOSPI200/S\&P500 시세·재무·뉴스 적재 |
| P2: L1 지표 \+ 검증 | 3주 | 20개 원자 지표 함수 \+ 단위/경계/횡단면 테스트 |
| P3: L2·L3 \+ Veto | 1주 | 카테고리 합성, Hard Filter, Veto Gate |
| P4: LLM Analyzer | 2주 | 차트 비전, 뉴스 요약, 정성 보정 프롬프트 튜닝 |
| P5: Reporter | 1주 | 한국어 일일 리포트 생성 |
| P6: Flutter MVP | 3주 | 9개 화면 (대시보드 우선, Indicator Inspector 포함) |
| P7: KIS 연동 | 1주 | 보유종목 조회 동기화 |
| P8: Shadow Port \+ 백테스트 | 2주 | vectorbt 백테스트, 가상 포트폴리오 추적 |
| P9: 캘리브레이션 | 지속 | 가중치·임계값 튜닝, 월간 리뷰 |

총 P0\~P8 약 16주. P9는 운영 단계의 지속 작업.

# **13\. 미해결 결정사항**

| 주제 | 옵션 | 결정 시점 |
| ----- | ----- | ----- |
| 일봉 시세 폴백 우선순위 | Alpaca / pykrx / 양쪽 병렬 | P1 |
| LLM 모델 | Gemini 2.5 Flash / Pro / Vertex AI | P4 |
| 차트 이미지 생성 | Cloud Run에서 matplotlib / Flutter에서 클라이언트 | P4 |
| 대시보드 레이아웃 | 카드 vs 리스트 vs 히트맵 | P6 |
| 관심종목 자동 추출 | 수동만 / Top Movers 자동 추가 | P6 |
| 과거 점수 보존 기간 | 1년 / 5년 / 영구 | P0 |
| KIS 토큰 갱신 실패 대응 | 재로그인 푸시 / 자동 폴백 (수동 입력) | P7 |
| Shadow Portfolio 시작 시점 | P3 직후 / P9 직전 | P3 |

*이 설계서는 v2.0 초안이다. v1과 달리 자동 매매를 제거하고 종목별 점수 기반 분석가 비서로 재정의되었다. 백테스트 결과 (P8)와 캘리브레이션 (P9)을 거치며 v3로 갱신될 예정이다.*
# Methodology

본 문서는 데이터 소스, 전처리, 변수 생성, 분석 절차를 간단히 요약합니다. 상세한 코드 내용은 `notebooks/01–03`를 참고하세요.

## 1) 연구 개요·질문
- **목표**: 앱 사용량(카테고리), 수면 지표와 정신건강 점수(PHQ-9, GAD-7, Stress) 간 관계를 탐색하고, **수면 상태가 관계를 조절**하는지 검증.
- **핵심 질문**
  1) 앱 사용량과 정신건강 점수 간 단순 상관이 존재하는가?
  2) 수면의 질(신뢰도)에 따라 그 관계의 기울기가 달라지는가?

## 2) 데이터 소스 (비공개)
- `앱 사용 로그`: `uid`, `week`, `category`, `duration(초)`
- `정신건강 설문`: `PHQ-9`, `GAD-7`, `Stress Questionnaire`(JSON 문항)
- `수면 데이터`: `meanConfidence`(수면 품질 신뢰도), `midawake_duration`(중간에 깬 시간)

> 원본 파일은 공개하지 않으며, 산출물만 제공됩니다.

## 3) 전처리 (01_data_preprocessing.ipynb)

### 3.1 설문 점수 산출
- JSON 문자열 파싱 후 각 문항의 선택지(Boolean 배열)에서 **첫 True의 인덱스**에 가중치 `[0,1,2,3]`(PHQ-9/GAD-7), `[0,1,2,3,4]`(Stress)를 부여해 **합산 점수**를 계산.

### 3.2 앱 사용 피벗 및 파생
- `uid×week×category`로 사용시간(초) 합계 → `uid×week` 행, **카테고리별 열**로 피벗.
- 모든 앱 시간 열을 **시간 단위**로 변환해 `*_hours` 파생.

### 3.3 수면 지표
- `meanConfidence`를 주차 평균으로 집계 → `mean_confidence_sleep`
- `midawake_duration`은 `"HH:MM:SS"`를 **분** 단위로 변환 후 주차 평균 → `midawake_duration_sleep`

### 3.4 정규화·조인·결측
- `week`를 문자열 정규화(예: `"8.0"`→`8`) 후 **정수**로 통일, `uid`는 문자열화.
- 조인 순서: `app_pivot ⨝ response`(inner) → `sleep`/`sleep_diary`(left).
- 결측: 수면 관련 열을 **전체 평균으로 대치**.
- `uid, week` 중복 제거.
- **출력**: `notebooks/results/tables/processed_weekly/` (Parquet).

## 4) 기술통계·상관 (02_correlation_analysis.ipynb)

- **기술통계**: 평균/표준편차/사분위수/중앙값 저장(→ `descriptive_stats.csv`).
- **분포 시각화**: 카테고리별 `*_hours` + 설문 점수 히스토그램(→ `dist_panels.png`).
- **상관분석**: Spearman(순위 기반)으로 `*_hours` ↔ `PHQ9/GAD7/Stress` 상관계수 산출
- **다중비교 보정**: Benjamini–Hochberg **FDR(q=0.05)**.  
- **보고 정책**:
  - **확증(가설 기반)**: 이론적으로 의미 있는 소수 쌍만 별도 FDR 적용.
  - **탐색**: 전 조합의 보정 전 Top-K를 **참고용**으로 작성

## 5) 회귀·조절효과 (03_regression_analysis.ipynb)

### 5.1 변수 변환
- `X` = 앱 카테고리 사용시간 `*_hours` (중심화),  
  `M` = 수면 신뢰도 `mean_confidence_sleep` (중심화),  
  `Y` ∈ {`PHQ9_score`, `GAD7_score`, `Stress_score`}.  
- 상호작용항 `X·M` 생성.

### 5.2 단계적 회귀 (각 카테고리·각 Y)
- **Step1**: `Y = β0 + β1 X + ε`  
- **Step2**: `Y = β0 + β1 X + β2 M + ε`  
- **Step3**: `Y = β0 + β1 X + β2 M + β3 (X·M) + ε`
- **표준오차**: 반복측정 고려를 위해 **cluster-robust SE (groups=uid)**.
- **다중공선성**: VIF 계산.  
- **결과물**: 계수표(`moderation_step3_APA.csv`), 조절 플롯(`moderation_*_*.png`).

## 6) 해석
- FDR 보정 하에서 전 조합 단순 상관은 유의하지 않을 수 있음(0이 많고 꼬리가 긴 분포 + 보정으로 인한 파워 감소).  
- 그러나 조절효과 분석에서 **SOCIAL/GAME × 수면 신뢰도**가 일부 지표에서 유의 → 수면 상태에 따라 앱 사용의 영향이 달라질 수 있음
- 낮은 R²는 다른 공변량을 고려하는 것의 필요성을 보여줌

## 7) 소프트웨어·환경
- Python 3.11/3.12, **PySpark 3.5.x**, pandas, numpy, scipy, statsmodels, pyarrow, matplotlib/seaborn.  
- 일부 환경에서 PySpark↔Python 3.12 조합은 `distutils` 이슈가 있어 `pyspark`, `setuptools`, `packaging` 최신 버전을 권장.

## 8) 재현 방법
1) `all_data/`에 원본 CSV 배치(비공개).  
2) `01 → 02 → 03` 노트북 순서 실행.  
3) `python scripts/build_results_summary.py` 실행 → `docs/results_summary.md` 생성.


## 9) 한계·윤리
- 세부 사항은 **[docs/limitations_ethics.md](limitations_ethics.md)** 참고.

# Methodology

본 문서는 데이터 소스, 전처리, 변수 생성, 분석 절차(Spearman + FDR, 조절 회귀)를 기술합니다. 구현은 `notebooks/01–03`에 대응합니다.

## 1) 연구 개요·질문
- **목표**: 앱 사용량(카테고리), 수면 지표와 정신건강 점수(PHQ-9, GAD-7, Stress) 간 관계를 탐색하고, **수면 상태가 관계를 조절**하는지 검증.
- **핵심 질문**
  1) 단순 상관(앱 사용량 ↔ 설문 점수)은 존재하는가?  
  2) 수면 신뢰도(평균)가 높고/낮음에 따라 그 관계의 **기울기**가 달라지는가?

## 2) 데이터 소스 (비공개)
- `filtering_complete_app_usage.csv`: `uid`, `week`, `category`, `duration(초)`.  
- `response_week_mapping_adjusted.csv`: `uid`, `week`, `PHQ-9`, `GAD-7`, `Stress Questionnaire`(문항 배열 JSON 문자열).  
- `sleep_week_mapped.csv`: `uid`, `week`, `meanConfidence`(수면 센서 신뢰도).  
- `sleep_diary_week_mapped.csv`: `uid`, `week`, `midawake_duration`(HH:MM:SS).

> 원본 파일은 공개하지 않으며, 분석 재현용 산출물만 제공됩니다.

## 3) 전처리 (01_data_preprocessing.ipynb)

### 3.1 설문 점수 산출
- JSON 문자열 파싱 후 각 문항의 선택지(Boolean 배열)에서 **첫 True의 인덱스**에 가중치 `[0,1,2,3]`(PHQ-9/GAD-7), `[0,1,2,3,4]`(Stress)를 부여해 **합산 점수**를 계산.

### 3.2 앱 사용 피벗 및 파생
- `uid×week×category`로 사용시간(초) 합계 → `uid×week` 행, **카테고리별 열**로 피벗.
- 모든 앱 시간 열을 **시간 단위**로 변환해 `*_hours` 파생.

### 3.3 수면 지표
- `meanConfidence`를 주차 평균.  
- `midawake_duration`은 `"HH:MM:SS"`를 **분** 단위로 변환 후 주차 평균.

### 3.4 정규화·조인·결측
- `week`를 문자열 정규화(예: `"8.0"`→`8`) 후 **정수**로 통일, `uid`는 문자열화.
- 조인: `app_pivot ⨝ response`(inner) → `sleep`/`sleep_diary`(left).
- 결측: 수면 관련 열을 **전체 평균으로 대치**.
- `uid, week` 중복 제거.
- **출력**: `notebooks/results/tables/processed_weekly/` (Parquet).

> 전처리 결과의 예시 규모: N ≈ 552 (`uid×week` 행, 프로젝트 시점 기준).

## 4) 기술통계·상관 (02_correlation_analysis.ipynb)

- **기술통계**: 평균/표준편차/사분위수/중앙값 저장(→ `descriptive_stats.csv`).
- **분포 시각화**: 카테고리별 `*_hours` + 설문 점수 히스토그램(→ `dist_panels.png`).
- **상관**: Spearman(순위 기반)으로 `*_hours` ↔ `PHQ9/GAD7/Stress`.  
- **다중비교 보정**: Benjamini–Hochberg **FDR(q=0.05)**.  
- **보고 정책**:
  - **확증(가설 기반)**: 이론적으로 의미 있는 소수 쌍만 별도 FDR 적용(옵션).
  - **탐색**: 전 조합의 보정 전 Top-K를 **참고용**으로 병기.

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

> 선택 분석: **within-person(디미닝)** 또는 혼합효과모형으로 개인 내 변동만 추정 가능.

## 6) 해석 가이드
- FDR 보정 하에서 전 조합 단순 상관은 유의하지 않을 수 있음(파워 손실 + 제로-많음·긴 꼬리).  
- 그러나 조절효과 분석에서 **SOCIAL/GAME × 수면 신뢰도**가 일부 지표에서 유의 → **맥락 의존적 관계** 시사.
- 낮은 R²는 추가 요인의 영향 가능성을 암시.

## 7) 소프트웨어·환경
- Python 3.11/3.12, **PySpark 3.5.x**, pandas, numpy, scipy, statsmodels, pyarrow, matplotlib/seaborn.  
- 일부 환경에서 PySpark↔Python 3.12 조합은 `distutils` 이슈가 있어 `pyspark`, `setuptools`, `packaging` 최신 버전을 권장.

## 8) 재현 안내
1) `all_data/`에 원본 CSV 배치(비공개).  
2) `01 → 02 → 03` 노트북 순서 실행.  
3) `python scripts/build_results_summary.py` 실행 → `docs/results_summary.md` 생성.

## 9) 한계·윤리
- 세부 사항은 **`docs/limitations_ethicss.md`** 참고.

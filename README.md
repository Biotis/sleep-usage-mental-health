## App Usage × Sleep ↔ Mental Health

스마트폰 앱 사용량(카테고리별), 수면 지표(신뢰도·밤중 깬 시간(분)), 정신건강 설문(PHQ-9/GAD-7/Stress)을 결합해 관계성을 분석했습니다.  
전처리는 **PySpark**, 분석은 **Spearman+FDR(다중비교 보정)** 및 **조절 회귀(클러스터-강건 SE)** 로 수행했습니다.  
**데이터는 비공개**이며, 코드와 결과물(표/그림)만 공개합니다.


(**보정** = 여러 항목을 동시에 비교할 때 생길 수 있는 우연을 줄이기 위해 p값을 조정(FDR 보정) 했다는 의미)

---

## Preview

<p float="left">
  <img src="notebooks/results/figures/dist_panels.png" width="49%" />
  <img src="notebooks/results/figures/spearman_heatmap.png" width="49%" />
</p>
<p float="left">
  <img src="notebooks/results/figures/moderation_SOCIAL_PHQ9_score.png" width="49%" />
  <img src="notebooks/results/figures/moderation_GAME_PHQ9_score.png" width="49%" />
</p>

자세한 표/요약 👉 **[docs/results_summary.md](docs/results_summary.md)**

---

## Hypothesis (연구 가설)
- **H_main(주효과)**: 앱 사용 시간이 늘수록 PHQ-9 / GAD-7 / Stress 점수가 **악화**된다.
- **H_mod(조절효과)**: 이 관계는 **수면의 질(mean_confidence)** 에 따라 **달라진다**
  (수면의 질이 높을수록 ‘정신 건강 악화 기울기’가 **완만**해지는 방향을 기대).

---

## Key Findings

- **H_main(주효과)**: 전반적·보정 포함 기준에서 **일관된 악화 효과는 확인되지 않음.**
  (0 값이 많고 일부 사용자만 매우 크게 쓰는 분포 특성 + 낮은 R²의 영향)
- **H_mod(조절효과)**: **수면의 질에 따라 효과가 달라지는 신호**가 일부 카테고리·지표에서 나타남
  - **SNS × 수면의 질** → PHQ-9 / GAD-7 / Stress 중 일부에서 **유의(p<.05)**  
  - **게임 × 수면의 질** → PHQ-9 / Stress에서 **유의(p<.05)**
  - 해석: **같은 사용 시간이라도, 잠을 잘 잔 날과 못 잔 날의 영향이 다를 수 있음.**
- **설명력**: R²는 낮음(≈0.01–0.03) → **다른 공변량 추가 및 모형 개선 여지**가 존재함.

> 보고 원칙: **가설 기반 비교(확증적)** = {SNS×수면, GAME×수면} × {PHQ-9, GAD-7, Stress} **6개**에만 **FDR 보정**을 적용하였음.
> 그 외 전수 탐색(다른 카테고리 전부)은 **보정 전 값 참고용**으로 별도로 기술하였음.


---

## Repository Layout

```
├── all_data/                         # (비공개)
├── notebooks/
│   ├── 01_data_preprocessing.ipynb   # Spark 전처리/통합/저장
│   ├── 02_correlation_analysis.ipynb # 기술통계/히스토그램/Spearman+FDR
│   └── 03_regression_analysis.ipynb  # 단계적 회귀(조절효과), cluster-robust SE
│   └── results/
│       ├── figures/                  # dist_panels, heatmap, moderation plots
│       └── tables/                   # descriptive_stats, spearman_fdr, moderation_step3_APA, VIF, …
├── docs/
│   ├── methodology.md                # 데이터/설계/지표 설명
│   ├── limitations_ethics.md        # 윤리/한계
│   └── results_summary.md            # 자동 생성된 결과 요약
├── scripts/
│   └── build_results_summary.py      # 결과 요약 MD 자동 생성 스크립트
├── requirements.txt                  # (참고) 의존성
└── LICENSE
```

---

## Methods

**01 전처리**  
- 설문 JSON 에서 점수 계산(PHQ-9 / GAD-7 / Stress) 
- 앱 사용 시간을 카테고리별 열로 정리(초 → 시간 단위 파생)
- 수면: 잠을 얼마나 잘 잤다고 느꼈는지(평균), 밤중에 깨어 있었던 시간(분) 계산
- 'week'/'uid' 형식 통일, 결측치는 평균으로 채움 → **Parquet 저장**

**02 상관/기술통계**  
- 분포/요약통계 확인, 상관분석 진행
- Spearman 상관관계분석 + **FDR(BH) 보정** (*가설 기반 vs 탐색적* 분리하여 확인)

**03 회귀(조절효과)**  
- 앱 사용 시간과 수면 지표를 **중심화**
- 앱 사용 시간 × 수면 지표 **상호작용**을 넣어, 수면 상태에 따라 영향이 달라지는지 확인   
- 단계적 회귀(Step1~3), **cluster-robust SE (groups=uid)**  
- VIF, 조절 플롯 저장
- **조절 변수**: 수면의 질(mean_confidence).  
- 상호작용: `AppCategory_*_hours(중심화) × 수면의 질(중심화)


---

## How to Run (데이터 비공개)

1) 데이터 위치

```
all_data/
├─ filtering_complete_app_usage.csv
├─ response_week_mapping_adjusted.csv
├─ sleep_week_mapped.csv
└─ sleep_diary_week_mapped.csv
```

2. 실행 순서
```
01_data_preprocessing.ipynb 실행 → notebooks/results/tables/processed_weekly/ 생성

02_correlation_analysis.ipynb 실행 → 표/그림 저장

03_regression_analysis.ipynb 실행 → 회귀 표/조절 플롯 저장
```
3. 요약 파일 생성
```
python scripts/build_results_summary.py
```

---

##  Key Artifacts
```
Figures:
notebooks/results/figures/dist_panels.png,
notebooks/results/figures/spearman_heatmap.png,
notebooks/results/figures/moderation_*.png

Tables:
notebooks/results/tables/descriptive_stats.csv,
notebooks/results/tables/spearman_fdr.csv,
notebooks/results/tables/moderation_step3_APA.csv,
notebooks/results/tables/vif_by_category.csv
spearman_fdr_hypotheses.csv, spearman_exploratory_top.csv
```
---

## Ethics & Limitations

- 원본 데이터는 **비공개**(개인/민감정보 보호)  
- **앱을 전혀 안 쓰는 사람(0이 많음)**과 아주 오래 쓰는 소수가 함께 있어, 단순 상관관계분석으로는 관계가 약하게 보일 수 있음
- R² 낮음 → 다른 요인(예: 생활 패턴, 스트레스 요인 등)이나 다른 분석 방법(로그 변환, 상위값 절제, 혼합모형 등)을 추가해 볼 여지가 존재함
- 자세한 내용: `docs/limitations_ethics.md`

---

## License

본 repository는 LICENSE 파일을 따릅니다. 원본 데이터는 포함되어 있지 않습니다.

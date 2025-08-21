## App Usage × Sleep ↔ Mental Health

스마트폰 앱 사용이 우울·불안·스트레스와 같은 정신건강 지표에 어떤 영향을 미치는지, 그리고 **수면의 질이 이 관계를 어떻게 조절하는지**를 분석한 프로젝트입니다.

**데이터는 비공개**이며, 코드와 결과물(표/그림)만 공개합니다.

---

## Hypothesis (연구 가설)

**가설**:

“특정 카테고리의 앱 사용 시간이 증가할수록, 우울·불안·스트레스 지표가 악화되며, 이 관계는 사용자의 수면의 질에 따라 달라질 것이다.”

→ 즉, 앱 사용량(독립변수)과 정신건강 지표(종속변수) 사이의 관계는 **수면의 질(조절변수)** 에 의해 강화되거나 약화될 수 있다.

- **H_main(주효과)**: 앱 사용 시간이 늘수록 PHQ-9 / GAD-7 / Stress 점수가 **악화**된다.
- **H_mod(조절효과)**: 이 관계는 **수면의 질(mean_confidence)** 에 따라 **달라진다**
  (수면의 질이 높을수록 ‘정신 건강 악화 기울기’가 **완만**해지는 방향을 기대).

---

## Preview

자세한 표/요약 👉 [docs/results_summary.md](docs/results_summary.md)


> 분석 결과
<p float="left">
  <figure style="display:inline-block; width:49%">
    <figcaption align="center">- 앱 사용시간과 정신건강 점수 분포 (0이 많고 일부 극단치 존재)</figcaption>
    <img src="notebooks/results/figures/dist_panels.png" width="50%" />
  </figure>
  <figure style="display:inline-block; width:49%">
    <figcaption align="center">앱 사용 ↔ 정신건강 지표 Spearman 상관 (전반적으로 약한 상관)</figcaption>
    <img src="notebooks/results/figures/spearman_heatmap.png" width="50%" />
  </figure>
</p>

<p float="left">
  <figure style="display:inline-block; width:49%">
    <figcaption align="center">Social APP 사용 × 수면 질 → PHQ-9</figcaption>
    <img src="notebooks/results/figures/moderation_SOCIAL_PHQ9_score.png" width="50%" />
  </figure>
  <figure style="display:inline-block; width:49%">
    <figcaption align="center">Game APP 사용 × 수면 질 → PHQ-9 (좋은 수면은 완화, 나쁜 수면은 악화)</figcaption>
    <img src="notebooks/results/figures/moderation_GAME_PHQ9_score.png" width="50%" />
  </figure>
</p>

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

**데이터: 앱 사용 로그(카테고리별), 수면 기록(meanConfidence, midawake), 정신건강 설문(PHQ-9, GAD-7, Stress)**

**분석: Spearman 상관 + Benjamini–Hochberg FDR 보정, 조절 회귀(cluster-robust SE)**

**구현: PySpark 전처리 → pandas/scipy/statsmodels 분석**

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
- **주차별 데이터에서 특정 카테고리의 앱을 전혀 사용하지않는 사람(0이 많음)**과 아주 오래 쓰는 소수가 함께 있어, 단순 상관관계분석으로는 관계가 약하게 보일 수 있음
- R² 낮음 → 다른 요인(예: 생활 패턴, 스트레스 요인 등)이나 다른 분석 방법(로그 변환, 상위값 절제, 혼합모형 등)을 추가해 볼 여지가 존재함
- 자세한 내용: `docs/limitations_ethics.md`

---

## License

본 repository는 LICENSE 파일을 따릅니다. 원본 데이터는 포함되어 있지 않습니다.

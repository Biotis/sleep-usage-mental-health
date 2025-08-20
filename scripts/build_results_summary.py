# scripts/build_results_summary.py  (compact + fixes)
from pathlib import Path
import pandas as pd
import os

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / ("notebooks/results" if (ROOT / "notebooks/results").exists() else "results")
TBL, FIG, DOCS = RESULTS / "tables", RESULTS / "figures", ROOT / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

def to_md(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except Exception:
        return "```\n" + df.to_string(index=False) + "\n```"

# 1) 로드
desc = pd.read_csv(TBL / "descriptive_stats.csv")
corr = pd.read_csv(TBL / "spearman_fdr.csv")
mod  = pd.read_csv(TBL / "moderation_step3_APA.csv")

# 2) 정리: 인덱스 컬럼 정돈
if "Unnamed: 0" in desc.columns:
    desc = desc.rename(columns={"Unnamed: 0": "column"})

# 3) FDR 유의 상관 상위
if "p_fdr" in corr.columns:
    corr_sig = corr[corr["p_fdr"] < 0.05].copy()
    if not corr_sig.empty:
        corr_sig["abs_rho"] = corr_sig["rho"].abs()
        corr_top = (corr_sig.sort_values(["target", "abs_rho"], ascending=[True, False])
                    .groupby("target").head(5))
    else:
        corr_top = pd.DataFrame(columns=["feature","target","rho","p_fdr"])
else:
    corr_top = pd.DataFrame(columns=["feature","target","rho","p_fdr"])

# 4) 마크다운 조립
md = []
md.append("# Results Summary\n")
md.append(f"*Results base:* `{RESULTS}`\n")

md.append("## Key Descriptive Stats (top 10)\n")
md.append(to_md(desc.head(10)))

md.append("\n\n## Top Correlations (FDR < 0.05)\n")
if len(corr_top):
    md.append(to_md(corr_top[["feature","target","rho","p_fdr"]]))
else:
    md.append("_No significant correlations under FDR < 0.05._")

md.append("\n\n## Significant Moderation Effects (Step3, p<.05)\n")
mod_sig = mod[mod["Inter_p"] < 0.05].copy().sort_values(["Dependent","Inter_p"])
md.append(to_md(mod_sig[["Category","Dependent","R2","Inter_t","Inter_p"]])
          if len(mod_sig) else "_No significant interactions under p<.05._")

md.append("\n\n## Figures\n")
dist_rel  = os.path.relpath(FIG / "dist_panels.png", DOCS)
heat_rel  = os.path.relpath(FIG / "spearman_heatmap.png", DOCS)
if (FIG/"dist_panels.png").exists():
    md.append(f"![Distributions]({dist_rel})")
if (FIG/"spearman_heatmap.png").exists():
    md.append(f"\n\n![Spearman Heatmap]({heat_rel})")
    
# (선택) Hypotheses-only FDR & Exploratory section
h_file = TBL / "spearman_fdr_hypotheses.csv"
e_file = TBL / "spearman_exploratory_top.csv"

md.append("\n\n## Hypotheses-Only Correlations (FDR, limited pairs)\n")
if h_file.exists():
    h = pd.read_csv(h_file)
    md.append(to_md(h.sort_values(["target","p_fdr"]).head(12)))
else:
    md.append("_Run the hypotheses-only FDR cell in 02 to populate this section._")

md.append("\n\n## Exploratory Top-5 by |rho| (uncorrected, descriptive)\n")
if e_file.exists():
    e = pd.read_csv(e_file)
    md.append(to_md(e))
else:
    md.append("_Run the exploratory cell in 02 to populate this section._")


out = DOCS / "results_summary.md"
out.write_text("\n".join(md), encoding="utf-8")
print("✅ Wrote", out)
print("   using results at:", RESULTS)
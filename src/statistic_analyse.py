"""
Friedman: Are there any differences between the three models?
Wilcoxon signed-rank: Which two are different, specifically?
Holm: Why did the models comparison become non-significant?
rank-biserial r: How big is the difference?
bootstrap CI: How stable is the median?
Average Rank

"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import sys, numpy, pandas, scipy
import itertools

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH  = ROOT / "results/tables/edit_magnitude.csv"
STATS_PATH  = ROOT / "results/tables/stats.csv"
MEDIAN_PATH = ROOT / "results/tables/medians.csv"
FRIEDMAN_PATH = ROOT / "results/tables/friedman.csv"
ENV_PATH    = ROOT / "results/tables/env.txt"

CONDITIONS = ["human", "Qwen2.5-0.5B", "Qwen2.5-1.5B", "Qwen2.5-3B"]
MODELS = CONDITIONS[1:]
N_ITEMS = 200
SEED = 42
N_RESAMPLES = 4000

def load_table() -> pd.DataFrame:
    """Read the per-item edit magnitudes written by compute_magnitude.py.

    Returns a DataFrame indexed by sentence id, with one column per condition
    in CONDITIONS order. Every row holds all four conditions for the same
    sentence, which is what makes the paired tests valid.
    """
    df = pd.read_csv(INPUT_PATH, index_col="id")

    assert list(df.columns) == CONDITIONS, list(df.columns)
    assert len(df) == N_ITEMS, len(df)
    assert df.index.is_unique, df.index[df.index.duplicated()].tolist()

    # a missing cell would silently drop that sentence from a paired test
    assert not df.isna().any().any(), df[df.isna().any(axis=1)]

    # magnitude is a non-negative proportion; it can exceed 1 when the output
    # is longer than the source, but a negative value means a broken pipeline
    assert (df >= 0).all().all(), df[(df < 0).any(axis=1)]

    return df

def median_table(df, conditions):
    """
    Calculate the median edit distance for each model
    and return a table listing the medians along with their confidence intervals.
    """
    rows = []
    # median
    for c in conditions:
        med = df[c].median()
    # bootstrap CI
        res = stats.bootstrap((df[c].to_numpy(),),np.median,
                          confidence_level=0.95,
                          n_resamples=N_RESAMPLES,
                          method="percentile",
                          random_state=SEED,)
        ci_low = res.confidence_interval.low
        ci_hi = res.confidence_interval.high
        rows.append({
        "condition":c,
        "median":med,
        "ci_low":ci_low,
        "ci_hi":ci_hi,
        })

    out = pd.DataFrame(rows)
    return out

def friedman(df, conditions):
    # friedmanchisquare for each models
    results = stats.friedmanchisquare(*[df[c] for c in conditions])
    # freedom
    dof = len(conditions) - 1
    # average Rank
    ave_rank = df[conditions].rank(axis=1).mean()
    results_dict = {"chi2":float(results.statistic),
                    "p":float(results.pvalue),
                    "df":dof,
                    "mean_rank":ave_rank.to_dict()}
    ranks = df[conditions].rank(axis=1)
    k = len(conditions)
    assert (ranks.sum(axis=1) == k * (k + 1) / 2).all()
    return results_dict

def pairwise(df, conditions):
    """ By comparing all pairs of models, 
    we can determine whether their differences are significant. 
    return modelspair, n, p_raw, p_holm, r
    """
    rows = []
    for a, b in itertools.combinations(conditions, 2):
        d = df[a].to_numpy() - df[b].to_numpy()
        d = d[d != 0]
        n = len(d)

        res = stats.wilcoxon(df[a], df[b], zero_method="wilcox", correction=False,
                             method="approx")
        p_raw = res.pvalue
        ranks = stats.rankdata(np.abs(d))
        Wp = ranks[d > 0].sum()
        Wn = ranks[d < 0].sum()
        r = (Wp - Wn) / (Wp + Wn)
        assert np.isclose(Wp + Wn, n * (n + 1) / 2)
        
        rows.append({"cond_a":a,
                     "cond_b":b,
                      "n":n,
                       "p_raw": p_raw,
                       "r": r})
    out = pd.DataFrame(rows)

    # Holm correction across all six comparisons at once
    p = out["p_raw"].to_numpy()
    m = len(p)
    order = np.argsort(p)                    # indices, smallest p first
    adj = (m - np.arange(m)) * p[order]      # multipliers m, m-1, ..., 1
    adj = np.maximum.accumulate(adj)         # enforce monotonicity
    adj = np.minimum(adj, 1.0)               # cap at 1
    p_holm = np.empty(m)
    p_holm[order] = adj                      # scatter back to original order
    out["p_holm"] = p_holm

    return out[["cond_a", "cond_b", "n", "p_raw", "p_holm", "r"]]

def main():
    df = load_table()
    meds = median_table(df, CONDITIONS)
    fr3 = friedman(df, MODELS)
    fr4 = friedman(df, CONDITIONS)
    pw =pairwise(df, CONDITIONS)
    meds.to_csv(MEDIAN_PATH, index=False, float_format="%.6g")
    pw.to_csv(STATS_PATH, index=False, float_format="%.6g")
    fr = pd.DataFrame([
    {"test": "3 models",    **fr3},
    {"test": "4 conditions", **fr4},
    ])
    fr.to_csv(FRIEDMAN_PATH, index=False, float_format="%.6g")
    ENV_PATH.write_text("\n".join([
        "# environment",
        f"python  : {sys.version.split()[0]}",
        f"numpy   : {np.__version__}",
        f"pandas  : {pd.__version__}",
        f"scipy   : {scipy.__version__}",
        "",
        "# settings",
        f"SEED        = {SEED}",
        f"N_RESAMPLES = {N_RESAMPLES}",
        "",
        "# test configuration",
        "friedman  : scipy.stats.friedmanchisquare (tie correction applied)",
        "wilcoxon  : zero_method=wilcox, correction=False, method=approx",
        "holm      : all pairwise comparisons corrected as one family",
        "bootstrap : method=percentile, confidence_level=0.95",
    ]) + "\n")

    print("=== medians, 95% bootstrap CI ===")
    print(meds.to_string(index=False))
    print("\n=== Friedman ===")
    print(fr.to_string(index=False))
    print("\n=== pairwise Wilcoxon signed-rank, Holm-corrected ===")
    print(pw.to_string(index=False))
    print(f"\nwritten: {MEDIAN_PATH.name}, {FRIEDMAN_PATH.name}, "
          f"{STATS_PATH.name}, {ENV_PATH.name}")
    


if __name__ == "__main__":
    main()
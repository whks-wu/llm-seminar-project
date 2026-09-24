from pathlib import Path
import difflib
import pandas as pd
import csv, re, difflib, statistics

ROOT = Path(__file__).resolve().parent.parent
RESULT_PATH = ROOT / "results/pilot_outputs_qwensfamily_02_200.csv"
MANUAL_PATH = ROOT / "notes/preamble_suffix_manual.csv"
OUTPUT_PATH = ROOT / "results/tables/edit_magnitude.csv"

MODELS = ["Qwen2.5-0.5B", "Qwen2.5-1.5B", "Qwen2.5-3B"]
N_ITEMS = 200
PREAMBLE_COUNTS = {"Qwen2.5-0.5B": 7, "Qwen2.5-1.5B": 15}
SUFFIX_COUNTS = {"Qwen2.5-1.5B": 2, "Qwen2.5-3B": 5}
CLITICS = ["'s", "n't", "'re", "'ve", "'ll", "'d", "'m"]
PUNCTUATION = ',.!?;:()"'
PUNCT_RE = re.compile("([" + re.escape(PUNCTUATION) + "])")

def load_data():
    """Read the generation results and the manual annotations of model
    commentary, join them, and check that the data is shaped the way the
    analysis assumes.

    Returns the 600-row long table with two extra columns: `preamble` and
    `suffix`.
    """
    df = pd.read_csv(RESULT_PATH)

    assert set(df["model"]) == set(MODELS), sorted(set(df["model"]))

    per_model = df.groupby("model").size()
    assert (per_model == N_ITEMS).all(), per_model.to_dict()

    id_sets = {m: set(g["id"]) for m, g in df.groupby("model")}
    reference = id_sets[MODELS[0]]
    assert len(reference) == N_ITEMS, len(reference)
    for m in MODELS[1:]:
        assert id_sets[m] == reference, sorted(id_sets[m] ^ reference)

    # `source` and `gold_correction` are stored once per model, so each id has
    # three copies. They must agree: the human baseline is taken from one copy.
    spread = df.groupby("id")[["source", "gold_correction"]].nunique()
    assert (spread == 1).all().all(), spread[(spread != 1).any(axis=1)]

    # run_pilot.py writes a message here when a generation fails
    assert df["error"].isna().all(), df.loc[df["error"].notna(), ["id", "model", "error"]]

    # the manual annotations
    manual = pd.read_csv(MANUAL_PATH, dtype=str)
    assert list(manual.columns) == ["id", "model", "preamble", "suffix"], list(manual.columns)
    assert not manual.duplicated(["id", "model"]).any(), \
        manual[manual.duplicated(["id", "model"], keep=False)]
    assert set(manual["model"]) <= set(MODELS), sorted(set(manual["model"]) - set(MODELS))
    # a row that records neither a preamble nor a suffix annotates nothing
    assert (manual["preamble"].notna() | manual["suffix"].notna()).all(), \
        manual[manual["preamble"].isna() & manual["suffix"].isna()]

    # join 
    n_before = len(df)
    df = df.merge(manual, on=["id", "model"], how="left", validate="one_to_one")
    assert len(df) == n_before, (n_before, len(df))

    pre_counts = df[df["preamble"].notna()].groupby("model").size().to_dict()
    assert pre_counts == PREAMBLE_COUNTS, pre_counts
    suf_counts = df[df["suffix"].notna()].groupby("model").size().to_dict()
    assert suf_counts == SUFFIX_COUNTS, suf_counts

    # the recorded clauses must really sit at the recorded end of the output —
    # this is what catches a mistyped id or a text the annotation no longer fits
    flagged = df[df["preamble"].notna()]
    ok = [out.strip().startswith(pre.strip())
          for out, pre in zip(flagged["parsed_output"], flagged["preamble"])]
    assert all(ok), flagged.loc[[not v for v in ok], ["id", "model"]]

    flagged = df[df["suffix"].notna()]
    ok = [out.strip().endswith(suf.strip())
          for out, suf in zip(flagged["parsed_output"], flagged["suffix"])]
    assert all(ok), flagged.loc[[not v for v in ok], ["id", "model"]]

    return df
    
def strip_commentary(text, pre, suf):
    """Remove the preamble from a model output."""
    text = text.strip()

    if not pd.isna(pre):
        pre = pre.strip()
        assert text.startswith(pre)
        text = text[len(pre):].strip()
    if not pd.isna(suf):
        suf = suf.strip()
        assert text.endswith(suf)
        text = text.removesuffix(suf).strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()
    return text

def normalize(text):
    """normalize the number of tokens in a model output and in corpus sentence."""
    s = text.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    # Number of tokens for standardized clitics
    for clitic in CLITICS:
        s = s.replace(clitic, " "+clitic)
    
    s = PUNCT_RE.sub(r" \1 ", s)
    return s.split()

def magnitude(src, out):
    a = normalize(src)
    b = normalize(out)
    if not a:
        return 0.0
    total = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a=a, b=b).get_opcodes():
        if tag != "equal":
            total += max(i2 - i1, j2 - j1)
    return round(total / len(a), 3)

def main():
    df = load_data()
    df["clean"] = df.apply(lambda r: strip_commentary(r.parsed_output, r.preamble, r.suffix), axis=1)
    assert (df["clean"].str.strip() != "").all(), df.loc[df["clean"].str.strip() == "", ["id", "model"]]
    df["mag"] = df.apply(lambda r: magnitude(r.source, r.clean), axis=1)
    df["human"] = df.apply(lambda r: magnitude(r.source, r.gold_correction), axis=1)
    assert df.groupby("id")["human"].nunique().max() == 1

    wide = df.pivot(index="id", columns="model", values="mag")
    human = df.groupby("id")["human"].first()
    out = pd.concat ([human, wide], axis=1)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_PATH, float_format="%.6f")

    # Number of preamble matches
    print(df[df.preamble.notna()].groupby("model").size())
    print(out.median())

    print(df.nlargest(5, "mag")[["id", "model", "mag"]])
if __name__ == "__main__":
    main()



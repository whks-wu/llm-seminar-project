#!/usr/bin/env python3
"""
export_for_errant.py — write the parallel plain-text files ERRANT needs.

Input : results/pilot_outputs_qwensfamily_02_200.csv
Output: results/errant/source.txt, gold.txt, hyp_<model>.txt
        one sentence per line, identical ordering in every file.

Why regenerate the reference instead of using A.dev.gold.bea19.m2
-----------------------------------------------------------------
The shipped M2 was built with spaCy 1.9.0 (corpus readme). Scoring it against edits
extracted by a modern ERRANT mixes two tokenisers and produces spurious mismatches.
Running errant_parallel over (source, gold) with the *same* ERRANT that processes the
model output puts both sides through identical tokenisation.

This also removes the need for the hand-written normalisation used in the first analysis:
spaCy tokenises "It 's" and "It's" to the same two tokens.

Usage:
    python src/export_for_errant.py
Then, in the ERRANT environment:
    source .venv-errant/bin/activate
    cd results/errant
    errant_parallel -orig source.txt -cor gold.txt          -out ref.m2
    errant_parallel -orig source.txt -cor hyp_Qwen2.5-0.5B.txt -out hyp_0.5B.m2
    errant_compare  -hyp hyp_0.5B.m2 -ref ref.m2
"""

import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
IN_PATH = ROOT / "results/pilot_outputs_qwensfamily_02_200.csv"
OUT_DIR = ROOT / "results/errant"

# Same preamble rule as the first analysis, applied identically to every condition.
PRE = re.compile(
    r'^(?:the corrected[^:]*|here (?:is|are)[^:]*|corrected[^:]*|the sentence[^:]*|'
    r'i apologize[^:]*|sure[^:]*|certainly[^:]*)\s*:\s*', re.I)


def clean(text):
    """Strip a framing preamble and flatten to a single line.

    ERRANT reads one sentence per line, so any newline in a model output would shift
    every subsequent line and silently misalign the whole file.
    """
    s = str(text).strip()
    s2 = PRE.sub("", s).strip()
    if "\n" in s2:
        s2 = s2.split("\n")[-1].strip()
    s2 = s2.strip('"“”').strip()
    s2 = re.sub(r"\s+", " ", s2 or s)
    return s2 or "."          # never emit a blank line


def main():
    d = pd.read_csv(IN_PATH).fillna("")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ids = sorted(d["id"].unique())          # fixed order shared by every file
    base = d.drop_duplicates("id").set_index("id")

    def write(name, lines):
        p = OUT_DIR / name
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return p, len(lines)

    p, n = write("source.txt", [re.sub(r"\s+", " ", str(base.loc[i, "source"])).strip() for i in ids])
    print(f"{p.name:<28} {n} lines")
    p, n = write("gold.txt", [re.sub(r"\s+", " ", str(base.loc[i, "gold_correction"])).strip() for i in ids])
    print(f"{p.name:<28} {n} lines")

    for model in sorted(d["model"].unique()):
        g = d[d["model"] == model].set_index("id")
        p, n = write(f"hyp_{model}.txt", [clean(g.loc[i, "parsed_output"]) for i in ids])
        print(f"{p.name:<28} {n} lines")

    # alignment check: every file must have the same number of lines
    counts = {f.name: len(f.read_text(encoding="utf-8").rstrip("\n").split("\n"))
              for f in sorted(OUT_DIR.glob("*.txt"))}
    assert len(set(counts.values())) == 1, f"line counts differ: {counts}"
    print(f"\nall files aligned at {set(counts.values()).pop()} lines -> {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
export_for_errant.py — write the parallel plain-text files ERRANT needs.

Input : results/pilot_outputs_qwensfamily_02_200.csv
        notes/preamble_suffix_manual.csv   (via compute_magnitude.load_data)
Output: results/errant/source.txt, gold.txt, hyp_<model>.txt
        one sentence per line, identical ordering in every file.

Why regenerate the reference instead of using A.dev.gold.bea19.m2
-----------------------------------------------------------------
The shipped M2 was built with spaCy 1.9.0 (corpus readme). Scoring it against edits
extracted by a modern ERRANT mixes two tokenisers and produces spurious mismatches.
Running errant_parallel over (source, gold) with the *same* ERRANT that processes the
model output puts both sides through identical tokenisation.

Why the cleaning is imported rather than reimplemented
------------------------------------------------------
The edit-magnitude analysis and the ERRANT analysis must see the same cleaned output,
or the two tables in the report describe two different post-processings. Both therefore
call compute_magnitude.strip_commentary with the same manual annotation file. The earlier
version of this script used its own regex, which stripped a different set of preambles,
removed no trailing commentary, and reduced multi-line outputs to their last line.

Usage:
    python src/export_for_errant.py
Then, in the ERRANT environment:
    source .venv-errant/bin/activate
    cd results/errant
    errant_parallel -orig source.txt -cor gold.txt                 -out ref.m2
    errant_parallel -orig source.txt -cor hyp_Qwen2.5-0.5B.txt     -out hyp_0.5B.m2
    errant_compare  -hyp hyp_0.5B.m2 -ref ref.m2
"""

import re
from pathlib import Path

from compute_magnitude import load_data, strip_commentary

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "results/errant"


def flatten(text):
    """Collapse all whitespace to single spaces.

    ERRANT reads one sentence per line, so a newline inside a model output would shift
    every following line and silently misalign the whole file. Newlines are treated as
    ordinary whitespace, not as a signal to keep only the last line: in A.dev.0898 the
    models put the letter's salutation ("Hello Riley,") on a line of its own, and taking
    the last line would delete three words that belong to the sentence.
    """
    return re.sub(r"\s+", " ", str(text)).strip()


def main():
    d = load_data()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    d["clean"] = d.apply(
        lambda r: strip_commentary(r.parsed_output, r.preamble, r.suffix), axis=1)

    ids = sorted(d["id"].unique())          # fixed order shared by every file
    base = d.drop_duplicates("id").set_index("id")

    def write(name, lines):
        assert all(lines), f"{name}: blank line would misalign the file"
        p = OUT_DIR / name
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{p.name:<28} {len(lines)} lines")

    write("source.txt", [flatten(base.loc[i, "source"]) for i in ids])
    write("gold.txt", [flatten(base.loc[i, "gold_correction"]) for i in ids])

    for model in sorted(d["model"].unique()):
        g = d[d["model"] == model].set_index("id")
        write(f"hyp_{model}.txt", [flatten(g.loc[i, "clean"]) for i in ids])

    # alignment check: every file must have the same number of lines
    counts = {f.name: len(f.read_text(encoding="utf-8").rstrip("\n").split("\n"))
              for f in sorted(OUT_DIR.glob("*.txt")) if not f.name.startswith("OLD_")}
    assert len(set(counts.values())) == 1, f"line counts differ: {counts}"
    print(f"\nall files aligned at {set(counts.values()).pop()} lines "
          f"-> {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

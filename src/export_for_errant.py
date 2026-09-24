#!/usr/bin/env python3
"""
export_for_errant.py — write the parallel plain-text files ERRANT needs.

Input : results/pilot_outputs_qwensfamily_02_200.csv
        notes/preamble_suffix_manual.csv   (via compute_magnitude.load_data)
Output: results/errant/source.txt, gold.txt, hyp_<model>.txt
        one sentence per line, identical ordering in every file.
"""

import re
from pathlib import Path

from compute_magnitude import load_data, strip_commentary

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "results/errant"


def flatten(text):
    """Collapse all whitespace to single spaces."""
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

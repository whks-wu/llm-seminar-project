#!/usr/bin/env python3
"""
manual verification of the M2 edit reconstruction.

Prints, for a random handful of items in data/processed/sample.jsonl:
  (A) what the M2 annotation SAYS should change, and
  (B) what ACTUALLY differs between `source` and `gold_correction`, computed
      independently with difflib.
"""

import difflib
import json
import random
import sys
from pathlib import Path

# Resolved relative to this file, so the script runs from any working directory.
SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data/processed/sample.jsonl"


def actual_changes(source, gold):
    """Word-level diff between the two strings, independent of the annotation."""
    a, b = source.split(), gold.split()
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag == "equal":
            continue
        before, after = " ".join(a[i1:i2]), " ".join(b[j1:j2])
        if tag == "delete":
            out.append(f'deleted  "{before}"')
        elif tag == "insert":
            out.append(f'inserted "{after}"')
        else:
            out.append(f'"{before}" -> "{after}"')
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None

    rows = [json.loads(line) for line in open(SAMPLE_PATH, encoding="utf-8")]
    picked = random.Random(seed).sample(rows, min(n, len(rows)))

    for item in picked:
        print("=" * 78)
        print(f"[{item['id']}]   {item['n_gold_edits']} annotated edit(s), "
              f"{item['n_tokens']} tokens")
        print(f"  source : {item['source']}")
        print(f"  gold   : {item['gold_correction']}")

        print("  (A) annotation says:")
        for e in item["gold_edits"]:
            corr = e["correction"]
            if e["start"] == e["end"]:
                what = f'insert "{corr}" at position {e["start"]}'
            elif corr == "":
                what = f'delete tokens [{e["start"]}:{e["end"]}]'
            else:
                what = f'replace tokens [{e["start"]}:{e["end"]}] with "{corr}"'
            print(f'        {e["type"]:<16} {what}')

        print("  (B) source -> gold actually differs by:")
        changes = actual_changes(item["source"], item["gold_correction"])
        for c in changes or ["(nothing — this is a bug)"]:
            print(f"        {c}")

        flag = "" if len(changes) == item["n_gold_edits"] else \
               "   <-- counts differ, inspect (may be legitimate: adjacent edits merge)"
        print(f"  edits annotated: {item['n_gold_edits']}   "
              f"diffs found: {len(changes)}{flag}")
    print("=" * 78)
    print("""
What to look for:
  1. Does `gold` read as plausible English? Garbled word order, duplicated or truncated
     words mean apply_edits() has an offset bug.
  2. Does (B) match (A)? Same words, same direction. If the annotation says delete "at"
     but the diff shows a different word vanished, the offsets are off by one.
  3. Is the correction MINIMAL — only the flagged error touched, nothing else rewritten?
  4. Count mismatches are not automatically wrong: two adjacent edits can merge into one
     diff region. Read those cases rather than trusting the number.
""")

if __name__ == "__main__":
    main()

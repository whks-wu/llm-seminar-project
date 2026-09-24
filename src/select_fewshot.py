#!/usr/bin/env python3
"""
sample few-shot demonstration examples from the TRAINING split.
"""

import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_data import parse_m2, apply_edits          # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAIN_PATH = REPO_ROOT / "data/raw/wi+locness/m2/A.train.gold.bea19.m2"
OUT_PATH = REPO_ROOT / "notes/fewshot_examples.json"

MIN_TOKENS, MAX_TOKENS = 8, 18
SEED = 42

# How many examples to draw at each edit count. Chosen to approximate the corpus
# distribution in the 8-18 token band (roughly 35% / 29% / 19% / 10% for 1/2/3/4 edits),
# rather than demonstrating a constant edit size.
QUOTA = {1: 3, 2: 2, 3: 2, 4: 1}

PUNCT_ORTH = {"M:PUNCT", "R:PUNCT", "U:PUNCT", "M:ORTH", "R:ORTH", "U:ORTH"}


def eligible(source, edits):
    n_tokens = len(source.split())
    if not (MIN_TOKENS <= n_tokens <= MAX_TOKENS):
        return False
    types = {e["type"] for e in edits}
    if any(t.startswith("UNK") for t in types):      # unclassifiable, often degenerate
        return False
    if types <= PUNCT_ORTH:                          # punctuation-only, as in D5
        return False
    return True


def degenerate(gold):
    """Reject reconstructions that came out as broken English.

    A few W&I annotations split a run-on sentence by inserting ". X" — but the M2 file is
    already sentence-segmented, so applying that edit to the fragment duplicates a word or
    strands a period ("It . It represents ..."). The corpus data is what it is; such items
    simply cannot serve as demonstrations of good correction.
    """
    tokens = gold.split()
    if gold.startswith("."):
        return True
    if len(tokens) > 2 and tokens[1] == ".":          # stranded first word
        return True
    if re.search(r"\b(\w+)\s+\.\s+\1\b", gold):     # "It . It"
        return True
    return False


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else SEED

    pools = {k: [] for k in QUOTA}
    for source, edits in parse_m2(TRAIN_PATH):
        if not edits or len(edits) not in pools:
            continue
        if not eligible(source, edits):
            continue
        gold = apply_edits(source, edits)
        if gold == " ".join(source.split()):          # no effective change
            continue
        if degenerate(gold):
            continue
        pools[len(edits)].append({
            "source": source,
            "gold": gold,
            "types": [e["type"] for e in edits],
            "n_edits": len(edits),
        })

    rng = random.Random(seed)
    chosen = []
    for n_edits, quota in sorted(QUOTA.items()):
        pool = pools[n_edits]
        if len(pool) < quota:
            raise SystemExit(f"only {len(pool)} candidates with {n_edits} edits")
        chosen.extend(rng.sample(pool, quota))
    rng.shuffle(chosen)                               # don't order by edit count

    OUT_PATH.write_text(json.dumps(
        {"seed": seed, "quota": QUOTA, "source_file": str(TRAIN_PATH.relative_to(REPO_ROOT)),
         "min_tokens": MIN_TOKENS, "max_tokens": MAX_TOKENS, "examples": chosen},
        indent=2, ensure_ascii=False), encoding="utf-8")

    total = sum(e["n_edits"] for e in chosen)
    print(f"seed {seed} · pools available: "
          + " · ".join(f"{k} edits:{len(v)}" for k, v in sorted(pools.items())))
    # Compare against the same length band the examples were drawn from. The test sample
    # (sample.jsonl) averages 2.83 edits, but it spans 5-40 tokens; longer sentences carry
    # more errors, so that figure is not the right reference for 8-18 token examples.
    band_edits = sum(n * len(v) for n, v in pools.items())
    band_count = sum(len(v) for v in pools.values())
    print(f"drew {len(chosen)} examples, mean {total/len(chosen):.2f} edits/sentence "
          f"(pool mean for {MIN_TOKENS}-{MAX_TOKENS} tokens, 1-4 edits: "
          f"{band_edits/band_count:.2f})\n")
    for i, e in enumerate(chosen, 1):
        print(f"{i}. ({e['n_edits']} edits: {', '.join(e['types'])})")
        print(f"   Original:  {e['source']}")
        print(f"   Corrected: {e['gold']}\n")
    print(f"written to {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

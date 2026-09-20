#!/usr/bin/env python3
"""
prepare_data.py — build the frozen stimulus set for the overcorrection experiment.

Input : data/raw/wi+locness/m2/A.dev.gold.bea19.m2
        (CEFR level A = A1+A2 learners, BEA-2019 dev split, 1037 sentences)
Output: data/processed/sample.jsonl
        N items, one JSON object per line, with fields:
          id               unique item id, e.g. "A.dev.0042"
          source           the learner's original sentence (MODEL INPUT)
          gold_correction  the annotator's corrected sentence (SCORING REFERENCE)
          gold_edits       [{start, end, type, correction}, ...] on source token indices
          n_gold_edits     number of real (non-noop) edits
          n_tokens         length of source in whitespace tokens

Why this file exists
--------------------
Every model sees exactly the same `source` strings, which makes the comparison PAIRED
(required for the Friedman / Wilcoxon analysis). `gold_correction` is what ERRANT scores
each model against, which is what makes recall (the capability gate) and false-positive
edits (the primary overcorrection measure) computable at all.

The sample is frozen with a fixed seed and committed to the repository so that results
are reproducible and so that "sentence 42" means the same sentence in every condition.

M2 format
---------
    S <whitespace-tokenised source sentence>
    A <start> <end>|||<type>|||<correction>|||REQUIRED|||-NONE-|||<annotator_id>
    <blank line ends the sentence block>

Token offsets are 0-based and end-exclusive into source.split().
    start == end        -> insertion   (M: missing)
    correction == ""    -> deletion    (U: unnecessary)
    otherwise           -> replacement (R:)
    "A -1 -1|||noop|||" -> sentence contains no errors

NOTE: the M2 file does NOT store the corrected sentence. It stores the source plus a list
of edit operations, so the corrected sentence must be reconstructed by applying them.

Usage
-----
    python src/prepare_data.py

Run from the repository root with the virtualenv active. No third-party dependencies.
"""

import hashlib
import json
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG — these encode the design decisions recorded in notes/decisions.md (D5).
# Change them here, not inline, and update D5 if you do.
# ---------------------------------------------------------------------------

# Paths are resolved relative to this file, not the shell's working directory, so the
# script runs correctly from anywhere (e.g. a VS Code terminal opened elsewhere).
REPO_ROOT = Path(__file__).resolve().parent.parent

M2_PATH = REPO_ROOT / "data/raw/wi+locness/m2/A.dev.gold.bea19.m2"
OUT_PATH = REPO_ROOT / "data/processed/sample.jsonl"

# The W&I licence (clause 6) permits publishing excerpts of FEWER THAN 100 WORDS. The
# sample contains ~3,500 words, so sample.jsonl is git-ignored and must never be pushed.
# The manifest below carries only item ids, the config, and a checksum — enough for anyone
# to download the corpus themselves and regenerate a byte-identical sample.
MANIFEST_PATH = REPO_ROOT / "data/processed/sample_manifest.json"

SAMPLE_SIZE = 200
RANDOM_SEED = 42          # fixed: do NOT reroll if you dislike the sample

MIN_TOKENS = 5            # D5: below this, length-normalised edit distance is unstable
MAX_TOKENS = 40           # D5: above this, CPU inference gets slow for the 3B model

# D5: drop sentences whose ONLY edits are punctuation or orthography. The research
# question is about grammar, and the corpus readme notes punctuation handling was
# arbitrary before release v2.0.
DROP_PUNCT_ONLY_SENTENCES = True

# D5 (settled 11.09): spelling and orthography edits are KEPT, in the reference and in the
# metrics. This follows BEA-2019 convention, where grammatical error correction includes
# spelling, and it keeps scoring unbiased.
#
# Do not set this to False. Removing SPELL/ORTH edits from gold_correction would leave the
# misspelling in the reference; a model that fixes the spelling would then differ from the
# reference and be scored as a FALSE POSITIVE, i.e. as "overcorrection". Large models fix
# spelling, small ones often do not, so that setting would bias the result toward the
# hypothesis for reasons unrelated to model behaviour.
#
# Every edit's type is preserved in the output, so a grammar-only secondary analysis remains
# possible at metric time without regenerating the sample.
KEEP_SPELL_ORTH_IN_GOLD = True

PUNCT_TYPES = {"M:PUNCT", "R:PUNCT", "U:PUNCT"}
ORTH_TYPES = {"M:ORTH", "R:ORTH", "U:ORTH"}
SPELL_TYPES = {"M:SPELL", "R:SPELL", "U:SPELL"}

# D5: keep UNK edits — ERRANT could not classify them, but they are real human edits and
# dropping them would leave gold_correction incomplete.
DROP_UNK_SENTENCES = False


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_m2(path):
    """Yield (source_string, edits) per sentence block.

    edits is a list of dicts with keys start, end, type, correction, annotator.
    noop markers are dropped, so a clean sentence yields an empty list.
    """
    source, edits = None, []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if line.startswith("S "):
                source, edits = line[2:], []
            elif line.startswith("A "):
                fields = line[2:].split("|||")
                offsets = fields[0].split()
                edit_type = fields[1]
                if edit_type == "noop":
                    continue
                edits.append({
                    "start": int(offsets[0]),
                    "end": int(offsets[1]),
                    "type": edit_type,
                    "correction": fields[2],
                    "annotator": fields[5] if len(fields) > 5 else "0",
                })
            elif line == "" and source is not None:
                yield source, edits
                source, edits = None, []
    if source is not None:
        yield source, edits


def apply_edits(source, edits):
    """Reconstruct the corrected sentence by applying edits to the source tokens.

    Offsets refer to positions in the ORIGINAL token list, so edits are applied
    right-to-left; that way earlier offsets are still valid when we reach them.
    Ties are applied in reverse listing order so that two insertions at the same
    position keep their original relative order in the output.
    """
    tokens = source.split()
    ordered = sorted(edits, key=lambda e: (e["start"], e["end"]))
    for edit in reversed(ordered):
        start, end = edit["start"], edit["end"]
        if start < 0:                      # defensive: noop should already be filtered
            continue
        if not (0 <= start <= end <= len(tokens)):
            raise ValueError(
                f"edit span [{start}:{end}] out of bounds for {len(tokens)} tokens"
            )
        tokens[start:end] = edit["correction"].split()
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def keep_sentence(source, edits):
    """Apply the D5 inclusion criteria. Returns (bool, reason_if_rejected)."""
    if not edits:
        return False, "noop"

    n_tokens = len(source.split())
    if n_tokens < MIN_TOKENS:
        return False, "too_short"
    if n_tokens > MAX_TOKENS:
        return False, "too_long"

    types = {e["type"] for e in edits}
    if DROP_PUNCT_ONLY_SENTENCES and types <= (PUNCT_TYPES | ORTH_TYPES):
        return False, "punct_or_orth_only"
    if DROP_UNK_SENTENCES and any(t.startswith("UNK") for t in types):
        return False, "contains_unk"

    return True, None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not M2_PATH.exists():
        raise SystemExit(f"Corpus not found at {M2_PATH}.")

    kept, rejected = [], {}
    for index, (source, edits) in enumerate(parse_m2(M2_PATH)):
        if not KEEP_SPELL_ORTH_IN_GOLD:
            edits = [e for e in edits if e["type"] not in (SPELL_TYPES | ORTH_TYPES)]

        ok, reason = keep_sentence(source, edits)
        if not ok:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue

        gold = apply_edits(source, edits)

        # Some ERRANT UNK annotations record a "correction" identical to the source
        # (e.g. 'pasted' -> 'pasted'): the annotator flagged a span but no actual
        # correction is recoverable. Recall can never exceed 0 on these, so they would
        # sit in the data as permanent failures for every model. Drop them.
        if gold == " ".join(source.split()):
            rejected["no_effective_change"] = rejected.get("no_effective_change", 0) + 1
            continue

        # Sanity check: applying zero edits must be the identity. Cheap, catches a
        # whole class of off-by-one mistakes in apply_edits().
        assert apply_edits(source, []) == " ".join(source.split())

        kept.append({
            "id": f"A.dev.{index:04d}",
            "source": source,
            "gold_correction": gold,
            "gold_edits": [
                {k: e[k] for k in ("start", "end", "type", "correction")} for e in edits
            ],
            "n_gold_edits": len(edits),
            "n_tokens": len(source.split()),
        })

    if len(kept) < SAMPLE_SIZE:
        raise SystemExit(f"Only {len(kept)} eligible sentences; need {SAMPLE_SIZE}.")

    rng = random.Random(RANDOM_SEED)
    sample = rng.sample(kept, SAMPLE_SIZE)
    sample.sort(key=lambda item: item["id"])          # stable, readable ordering

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        for item in sample:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")

    digest = hashlib.sha256(OUT_PATH.read_bytes()).hexdigest()
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump({
            "description": "Reproducibility manifest. The corpus text itself is not "
                           "redistributed (W&I licence clause 6 permits excerpts under "
                           "100 words only). Download W&I+LOCNESS v2.1 as described in "
                           "README.md and run this script to regenerate sample.jsonl.",
            "source_file": str(M2_PATH.relative_to(REPO_ROOT)),
            "sample_size": SAMPLE_SIZE,
            "random_seed": RANDOM_SEED,
            "filters": {
                "min_tokens": MIN_TOKENS,
                "max_tokens": MAX_TOKENS,
                "drop_punct_only_sentences": DROP_PUNCT_ONLY_SENTENCES,
                "keep_spell_orth_in_gold": KEEP_SPELL_ORTH_IN_GOLD,
                "drop_unk_sentences": DROP_UNK_SENTENCES,
            },
            "eligible_after_filtering": len(kept),
            "rejected": rejected,
            "item_ids": [item["id"] for item in sample],
            "sample_jsonl_sha256": digest,
        }, fh, indent=2)
    print(f"manifest                 : {MANIFEST_PATH}")
    print(f"sample.jsonl sha256      : {digest[:16]}...")

    # ----- summary -----------------------------------------------------------
    print(f"eligible after filtering : {len(kept)}")
    print(f"rejected                 : {rejected}")
    print(f"written                  : {len(sample)} -> {OUT_PATH}")
    edits_per = [item["n_gold_edits"] for item in sample]
    toks = [item["n_tokens"] for item in sample]
    print(f"edits/sentence           : min {min(edits_per)}  "
          f"mean {sum(edits_per)/len(edits_per):.2f}  max {max(edits_per)}")
    print(f"tokens/sentence          : min {min(toks)}  "
          f"mean {sum(toks)/len(toks):.1f}  max {max(toks)}")
    print("\n--- first 2 items, eyeball these ---")
    for item in sample[:2]:
        print(f"\n[{item['id']}]")
        print(f"  source: {item['source']}")
        print(f"  gold  : {item['gold_correction']}")
        print(f"  edits : {[(e['type'], e['correction']) for e in item['gold_edits']]}")


if __name__ == "__main__":
    main()

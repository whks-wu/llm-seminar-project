"""
run_pilot.py — run every (model x prompt variant x sentence) combination and record
the raw and parsed outputs.

Inputs : data/processed/sample.jsonl (first N_ITEMS rows)
         PROMPTS from prompts.py
         MODELS, load, correct_sentence from load_models.py
Outputs: results/pilot_outputs.csv
         results/rendered_prompt_example.txt  (one example per variant, for the report)

Models are loaded once each and released afterwards: the outer loop is over models, not
over sentences, so the 3B model is not reloaded 40 times.

Usage:
    python src/run_pilot.py

To reuse for the full run, change N_ITEMS, VARIANTS and OUT_PATH below — the logic is
unchanged, so no second script is needed.
"""

import gc
import time
import torch
from load_models import MODELS, load, correct_sentence
from prompts import PROMPTS
import pandas as pd
from pathlib import Path

N_ITEMS = 200
VARIANTS = ["zero-shot"]

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "results/pilot_outputs_qwensfamily_02_200.csv"
RE_PROMPT_PATH = ROOT / "results/rendered_prompt_example.txt"
SAMPLE_PATH = ROOT / "data/processed/sample.jsonl"

df = pd.read_json(SAMPLE_PATH, lines=True)
sentences = df.head(N_ITEMS)


def write_prompt_examples(sentences):
    """Record one fully rendered prompt per variant.

    The prompt depends only on the variant and the sentence, never on the model, so one
    example per variant is enough. This file is what gets quoted in the report as
    "what the model actually received".
    """
    first = sentences.iloc[0]
    with open(RE_PROMPT_PATH, "w", encoding="utf-8") as f_p:
        for variant in VARIANTS:
            rendered = PROMPTS[variant]["template"].format(sentence=first["source"])
            f_p.write(f"{'=' * 70}\nVARIANT: {variant}   (item {first['id']}, "
                      f"stop={PROMPTS[variant]['stop']!r})\n{'=' * 70}\n")
            f_p.write(rendered)
            f_p.write("\n\n")
    print(f"prompt examples -> {RE_PROMPT_PATH.relative_to(ROOT)}")


def pilot(sentences):
    OUT_PATH.unlink(missing_ok=True)
    write_prompt_examples(sentences)

    total = len(MODELS) * len(VARIANTS) * len(sentences)
    done, failures, run_start = 0, 0, time.time()

    for name in MODELS:
        rows = []
        print(f"\n{'=' * 60}\n{name}\n{'=' * 60}")
        t_load = time.time()
        tok, m = load(name)
        print(f"  loaded in {time.time() - t_load:.1f}s")

        for variant in VARIANTS:
            print(f"  -- {variant} --")
            for _, row in sentences.iterrows():
                prompt = PROMPTS[variant]["template"].format(sentence=row["source"])
                n_src = len(tok(row["source"])["input_ids"])
                max_new = int(n_src * 1.5) + 10

                # One failing combination must not cost the whole model's results. The
                # error text is recorded instead, so the CSV itself shows which
                # (model, variant) pairs could not run at all.
                t0 = time.time()
                try:
                    raw = correct_sentence(
                        tok, m, prompt,
                        MODELS[name]["is_chat"],
                        MODELS[name]["generate_kwargs"],
                        max_new_tokens=max_new,
                    )
                    error = ""
                except Exception as exc:
                    raw, error = "", f"{type(exc).__name__}: {exc}"
                    failures += 1
                t1 = time.time()

                stop = PROMPTS[variant]["stop"]
                parsed = raw.split(stop)[0].strip() if stop else raw.strip()

                rows.append({
                    "id": row["id"],
                    "model": name,
                    "variant": variant,
                    "source": row["source"],
                    "gold_correction": row["gold_correction"],
                    "raw_output": raw,
                    "parsed_output": parsed,
                    "seconds": round(t1 - t0, 2),
                    "max_new_tokens": max_new,
                    "error": error,
                })

                done += 1
                mark = "!" if error else " "
                print(f"   {mark}[{done:3d}/{total}] {row['id']}  "
                      f"{t1 - t0:5.1f}s  {(error or parsed)[:60]!r}")

        pd.DataFrame(rows).to_csv(
            OUT_PATH, mode="a", header=not OUT_PATH.exists(), index=False)
        print(f"  wrote {len(rows)} rows -> {OUT_PATH.relative_to(ROOT)}")

        # release models
        del m, tok
        gc.collect()  # a memory management technique, automatically reclaim memory
        torch.mps.empty_cache()

    elapsed = time.time() - run_start
    print(f"\n{'=' * 60}")
    print(f"done: {done} generations in {elapsed / 60:.1f} min "
          f"({elapsed / done:.1f}s each), {failures} failed")
    out = pd.read_csv(OUT_PATH)
    print(f"CSV: {len(out)} rows")
    print(out.groupby(["model", "variant"])["seconds"].agg(["count", "mean"]).round(1))


def main():
    pilot(sentences)


if __name__ == "__main__":
    main()

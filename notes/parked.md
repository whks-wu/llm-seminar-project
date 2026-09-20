# Parked ideas

Things worth doing, deliberately not started yet. Revisit only when the current
main line is finished AND analysed.

---

## P1 — Small locally-runnable instruction-tuned models (Part 2)

**Parked 14.09. Unblock condition: Part 1 (three conditions, few-shot) has been run,
scored, and analysed. Not before.**

### Why this belongs in the project

The original motivation in my project draft was *low-cost, locally runnable educational
AI* — "faster response and lower computational costs (or even no cost at all)". The
three-condition design drifted away from that into a pure pretraining-scale question.
Adding small instruction-tuned models brings the practical motivation back.

### What it also fixes in the design

Qwen2.5-3B vs Qwen2.5-0.5B are the **same model family, same pretraining data, both
instruction-tuned** — only parameter count differs. That is the clean parameter-scale
contrast the design has been missing. The GPT-2 control is not clean in this way, because
architecture, tokenizer, objective and training recipe all differ from GPT-BERT as well.

So this is not only a motivation patch; it strengthens the comparison.

### Candidates (all run on an M-series Mac)

- `Qwen/Qwen2.5-0.5B-Instruct` — same family as condition 3, best for the scale contrast
- `meta-llama/Llama-3.2-1B-Instruct` — gated on HF, needs licence acceptance
- `HuggingFaceTB/SmolLM2-360M-Instruct` — smallest, ungated
- `google/flan-t5-base` — instruction-tuned seq2seq, 250M (different architecture: would
  need a separate code path, probably not worth it)

**Add one, at most two.** More than that cannot be analysed or fitted on a poster.

### Why it is cheap

Adding a model is one entry in the `MODELS` dict in `src/load_models.py`. `load()` and
`correct_sentence()` need no changes — that is the payoff from putting per-model
differences in config rather than in code.

### What it is NOT

These models are small in **parameters**, not in **training data** (Qwen2.5-0.5B still saw
~18T tokens). They cannot substitute for BabyLM and they do not answer the training-data
question. They answer a different one: *among models a learner could actually run for free
on their own laptop, which overcorrects least?*

### Cost to be honest about

- A second experiment means more analysis, more figures, more report space.
- The 2-page limit is hard. Part 2 probably has to be a short "practical implications"
  subsection rather than a co-equal second experiment.
- As of 14.09 there are ~7 sessions left and Part 1's pilot has not run. **This is a
  stretch goal, not a plan item.**


gpt-bert-babylm-small "max_position_embeddings": 512


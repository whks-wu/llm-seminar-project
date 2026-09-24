# Method: technical record

**This file is NOT report prose.** It records parameters, formulas and numbers so that
the method section can be written from facts rather than memory, and so the analysis is
reproducible. Write the actual text yourself.

Analysis date: 20.09.2026 · Data: `results/pilot_outputs_qwensfamily_02_200.csv`

---

## 1. Materials

- Corpus: W&I+LOCNESS v2.1 (BEA-2019), CEFR level A dev split, `A.dev.gold.bea19.m2`
- 1037 sentences -> 705 eligible -> **200 sampled**, `random_state = 42`
- Filters: 5-40 tokens; >=1 non-noop edit; punctuation/orthography-only excluded;
  14 degenerate items dropped (recorded correction identical to source)
- Gold corrections reconstructed by applying M2 edit operations (see `prepare_data.py`);
  manually verified, 0 reconstruction errors
- Reproducibility: `data/processed/sample_manifest.json` (seed, filters, ids, SHA-256).
  Corpus text not redistributed — W&I licence clause 6 allows excerpts under 100 words.

## 2. Conditions

| Condition | Params | Pretraining | Instruction-tuned |
|---|---|---|---|
| Qwen2.5-0.5B-Instruct | 0.5B | ~18T tokens | yes |
| Qwen2.5-1.5B-Instruct | 1.5B | ~18T tokens | yes |
| Qwen2.5-3B-Instruct | 3.1B | ~18T tokens | yes |

Same family throughout: pretraining corpus, instruction tuning, architecture and tokenizer
held constant; **only parameter count varies**.

Human annotator corrections serve as a fourth (non-model) reference point.

## 3. Generation

- Zero-shot only. Prompt: see `src/prompts.py` and `results/rendered_prompt_example.txt`
- Chat template applied via `tokenizer.apply_chat_template(..., add_generation_prompt=True)`
- **Greedy decoding** (`do_sample=False`) — deterministic, reproducible
- `temperature`, `top_p`, `top_k` explicitly set to None (models ship sampling defaults)
- `max_new_tokens = int(1.5 * len(tokenize(source))) + 10`, computed per item with the
  model's own tokenizer
- 200 items x 3 models = **600 generations, 0 failures**
- Runtime: 0.43 / 0.91 / 1.59 s per item (0.5B / 1.5B / 3B), Apple Silicon, MPS

## 4. Post-processing (applied identically to all three conditions)

**(a) Preamble and suffix removal.** Some outputs prefix the correction with a framing clause.
Preamble 7/200 (0.5B), 15/200 (1.5B), 0/200 (3B)
suffix 0/200 (0.5B), 2/200 (1.5B), 5/200 (3B)
I manually searched for the prefaces and suffix myself in pilot_outputs_qwensfamily_02_200.csv, and then extracted them separately and saved them in preamble_suffix_manual.csv.

**(b) Tokenisation normalisation.** The corpus is pre-tokenised (`It 's`, punctuation as
separate tokens); model output is natural text (`It's`). Without normalisation these
differences count as edits. Steps: unify quote characters; remove space before punctuation;
split clitics (`'s`, `n't`, `'re`, ...) into separate tokens; separate punctuation;
lowercase. Applied to source, gold and model output alike.

**Effect (same 200 items): median edit magnitude fell from 0.375-0.438 to 0.167-0.244.**
43-56% of the raw distance was tokenisation artefact, not model behaviour.

**Caveat to state:** (a) and (b) are hand-Manual, line-by-line review, not ERRANT/spaCy. Results
are sensitive to them. ERRANT tokenises both sides with spaCy and is the proper tool.

### Why the shipped gold M2 was NOT used as the ERRANT reference

The corpus readme states the M2 files were generated with **spaCy v1.9.0** and
`en_core_web_sm-1.2.0`. Scoring them against edits extracted by a modern ERRANT (spaCy 3.x)
mixes two tokenisers and produces spurious mismatches.

Instead, the reference M2 was regenerated from (source, gold) plain text with the *same*
ERRANT installation that processes the model output:

    errant_parallel -orig source.txt -cor gold.txt -out ref.m2

Both sides therefore pass through identical tokenisation and edit extraction. This also
removes the need for the hand-written normalisation in (b) for the ERRANT-based metrics —
spaCy tokenises `It 's` and `It's` to the same two tokens. See `src/export_for_errant.py`.

### Corpus facts verified from primary sources (not inferred)

- **No annotation guidelines are published.** Checked: the BEA-2019 shared-task page,
  Yannakoudakis et al. (2018), the CLC annotation paper (Nicholls, English Profile Journal
  2011), and the corpus readme shipped with the data. None documents a minimal-edit policy.
  W&I+LOCNESS is *conventionally* treated as a minimal-edit corpus in the GEC literature,
  but that convention is not backed by a published annotation standard.
- **Gold M2 edit spans are ERRANT-derived, not human-authored.** The readme states the M2
  files were produced from character-level edits via `json_to_m2.py`. Annotators produced
  corrected *text*; the edit *spans* are algorithmic. Gold edit size is therefore not
  evidence that annotators chose to edit minimally.
- **Single annotator per text — verified empirically.** The JSON format supports multiple
  annotators and v2.1 updated the converter to handle them, so this was checked directly:
  A.dev 130/130 texts and A.train 1300/1300 texts have exactly one annotator.
- Fine-grained CEFR exists in the JSON but is dropped in the M2 files. A.dev splits as
  A1.i 22 · A1.ii 32 · A2.i 24 · A2.ii 52 texts. CEFR A is A1+A2, so the A-level M2 file
  already matches the research question; no action was needed.

## 5. Measure

Word-level edit magnitude, normalised by source length:

    align source and output with difflib.SequenceMatcher on token lists
    for every non-`equal` opcode, count max(len_source_span, len_output_span)
    divide the total by len(source)

Normalising by length makes long and short sentences comparable (3 words changed in a
6-word sentence is not the same as 3 in a 30-word sentence).

## 6. Statistics

**Paired throughout** — the same 200 sentences pass through all three models, so
between-sentence variance is removed.

- **Friedman test** (non-parametric repeated-measures ANOVA): rank the three conditions, Friedman used parallel correction
  within each sentence, compare rank sums. df = k-1 = 2.
- **Post-hoc pairwise Wilcoxon signed-rank**: per-sentence differences, zeros dropped,
  absolute differences ranked, W+ vs W- compared. Normal approximation (n >= 144).
- **Holm correction** over the 6 comparisons: p-values sorted ascending, multiplied by
  m, m-1, ..., with monotonicity enforced. Controls family-wise error; less conservative
  than Bonferroni.
- **Effect size**: rank-biserial r = (W+ - W-)/(W+ + W-), range -1..+1.
  Convention: 0.1 small, 0.3 medium, 0.5 large.
- **95% CI for medians**: bootstrap, 4000 resamples with replacement, percentile method.

## 7. Results

### Edit magnitude (normalised, relative to source)

| Condition | median | mean | 95% CI (median) |
|---|---|---|---|
| Human annotator | 0.167 | 0.197 | [0.143, 0.200] |
| Qwen2.5-0.5B | 0.250 | 0.299 | [0.212, 0.255] |
| Qwen2.5-1.5B | 0.244 | 0.289 | [0.200, 0.273] |
| Qwen2.5-3B | 0.167 | 0.225 | [0.143, 0.200] |

### Omnibus

Friedman chi2(2) = **17.28**, p = **0.00018**.
Mean ranks: 0.5B = 2.12, 1.5B = 2.12, 3B = 1.76.

### Pairwise (Holm-corrected)

| Comparison | n | z | p_holm | r |
|---|---|---|---|---|
| 0.5B vs 1.5B | 155 | -0.66 | 0.507 | +0.06 |
| 0.5B vs 3B | 156 | -4.81 | 4.5e-06 | +0.44 |
| 1.5B vs 3B | 144 | -5.06 | 1.7e-06 | +0.49 |
| 0.5B vs human | 162 | -5.67 | 8.4e-08 | +0.51 |
| 1.5B vs human | 155 | -5.36 | 4.1e-07 | +0.50 |
| **3B vs human** | 148 | -2.19 | **0.056** | +0.21 |

**Pattern is a step, not a gradient:** 0.5B and 1.5B do not differ from each other and
both edit significantly more than the human annotator; 3B edits significantly less than
both and is **not significantly different from the human annotator after correction**.

Report 3B vs human honestly: uncorrected p = 0.028, Holm-corrected p = 0.056, i.e. **not
significant after correction**. Do not write "identical to human".

### Whether the edits are the right ones

For each item, with A = d(source, output), B = d(gold, output), C = d(gold, source):

| Condition | improved (B < C) | worse (B > C) | no change (A = 0) |
|---|---|---|---|
| Qwen2.5-0.5B | 18.5% | 65.0% | 4.5% |
| Qwen2.5-1.5B | 25.0% | 56.5% | 6.5% |
| Qwen2.5-3B | **37.5%** | 40.0% | 2.0% |

**In the majority of items all three models move the sentence further from the human
correction than the original was.** The size trend holds here too (3B improves twice as
often as 0.5B), but no condition improves more often than it harms.

## 8. Known limitations (all need stating)

1. **No correctness gate yet.** Edit magnitude alone cannot separate appropriate restraint
   from simply doing less. ERRANT recall/precision is required before claiming 3B is
   "appropriately conservative" rather than merely less active.
2. Post-processing (preamble rule, tokenisation) is hand-written; 1.5B is most affected
   by (a) since it had 14/200 preambles.
3. Single annotator per text (verified: all 130 dev and 1300 train texts have exactly one).
   Some apparent overcorrection may be valid alternative corrections.
4. Gold M2 edit spans are ERRANT-derived, not human-authored; no W&I annotation guidelines
   are published (checked: shared-task page, Yannakoudakis et al. 2018, CLC annotation paper).
5. No minimality criterion was given to the models (deliberate, see D6): instructing
   minimal editing would measure instruction-following rather than intrinsic tendency.
   Part of the observed variation may reflect differing default interpretations.
6. Single prompt, single decoding strategy, one model family. Generalisation across
   families and prompts untested.
7. Earlier conditions (BabyLM, GPT-2) could not perform the task at all — see
   `results/pilot_outputs_babylm.csv` and PLAN.md.

# Project plan v3 — re-baselined 10.09.2026 (evening)

**Overcorrection in models pretrained on differently-sized corpora**
Qiancao Jiang · LLMs as models of human sentence processing, SoSe26

Report due **Wed 30.09, 23:59** · Poster session early October
**Working target: everything drafted by Sun 20.09.** Polish 21.–29.09.

Sessions 09:00–11:30 (2.5 h). Nine scheduled + one reserve day:
Fri 11 · Sat 12 · *(Sun 13 reserve)* · Mon 14 · Tue 15 · Wed 16 · Thu 17 · Fri 18 · Sat 19 · Sun 20

v1 archived in `notes/PLAN-v1-archived.md`.

---

## Locked decisions — do not reopen

**Research question** (own wording, finalise Fri, 20 min max): whether models pretrained on
less data show a lower tendency to overcorrect A1/A2 learner sentences.

**Three conditions on one ordered scale of PARAMETER COUNT** (revised 16.09):

| # | Model | Params | Pretraining data | Instr.-tuned |
|---|---|---|---|---|
| 1 | `Qwen/Qwen2.5-0.5B-Instruct` | 0.5B | ~18T tokens | yes |
| 2 | `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | ~18T tokens | yes |
| 3 | `Qwen/Qwen2.5-3B-Instruct` | 3.1B | ~18T tokens | yes |

Same family throughout, so pretraining data, instruction tuning, architecture and tokenizer
are held constant and **only parameter count varies**. All three run locally on the Mac and
are free — which is the practical motivation from the original project draft.

**This changes the independent variable from training-data size to model size, so the
research question changes with it.** See `notes/decisions.md`.

### Why the original conditions were dropped (16.09)

The 20-sentence pilot (`results/pilot_outputs.csv`) shows that neither developmentally-
plausible-scale model can perform generative error correction at all:

| Condition | n | identical to input | raw contains "Original:" | length ratio | s/item |
|---|---|---|---|---|---|
| gpt2 few-shot | 20 | **18** | 20 | 1.00 | 0.4 |
| gpt-bert few-shot | 20 | 0 | 19 | 0.66 | 3.0 |
| gpt2 zero-shot | 20 | 0 | 0 | 1.80 | 0.4 |
| gpt-bert zero-shot | 20 | 0 | 0 | 1.65 | 0.9 |
| Qwen2.5-3B few-shot | 20 | 0 | 0 | 0.90 | 2.8 |
| Qwen2.5-3B zero-shot | 20 | 0 | 0 | 1.00 | 2.0 |

**The key observation for the report:** GPT-2 learned the few-shot *format* but not the
*task* — it reproduced the input verbatim on 18/20 items. Verbatim copying is zero edits,
which on a raw Levenshtein metric looks like *perfect* minimal editing. This is the
incapacity-vs-restraint confound made concrete, and it is why the ERRANT recall gate is
load-bearing rather than optional.

These conditions are **not** re-run at n=200. The pilot table is the evidence.

**Rule: no further reframing of the research question.** Park new ideas in `notes/parked.md`.

---

## Metrics and reporting structure (settled 10.09 — read before S5)

**The confound this exists to solve.** A model that edits little *because it cannot do the
task* is indistinguishable, on edit distance alone, from a model that edits little *because
its acceptability boundary is permissive*. Incapacity and restraint produce the same number.
The whole hypothesis depends on separating them.

**This is not a metric problem — it is a conditioning problem.** Levenshtein distance is a
fine measure of how much a model changed. The flaw is reporting it unconditionally.

**ERRANT supplies the fix.** Per sentence, per system, aligned against the gold M2:
true-positive edits (matched the annotator), false-positive edits (model edited where the
annotator did not), false-negative edits (model missed one). From those three counts:

- **Recall > 0** = the capability gate. Recall 0 ⇒ the model corrected nothing real and its
  edit distance says nothing about restraint.
- **False-positive edit rate** = a direct overcorrection measure needing *no* gate, since it
  counts only edits the annotator declined to make. Arguably a cleaner operationalisation of
  the construct than Levenshtein.
- **Precision / F0.5** = the standard comparable picture.

**Report in this order — no new metrics required:**
1. P / R / F0.5 per condition — establishes each model can do the task at all
2. FP edit rate — **primary** overcorrection measure
3. Length-normalised Levenshtein, **conditioned on recall > 0** — secondary
4. Lexical difficulty (new tokens outside an A1/A2 list), same conditioning

**Citable support for the framing:** the official BEA-2019 metric is ERRANT span-based
**F0.5**, which in the organisers' words "weights precision twice as much as recall." The
field's headline metric already assumes unnecessary corrections cost more than missed ones.
Cite it as an established convention — the paper follows CoNLL-2014 and does *not* argue the
rationale, so do not present it as a defended principle.

**Limitation to state, not solve:** with singly-annotated dev data an ERRANT false positive
may be a valid alternative correction the annotator simply did not make, rather than an
overcorrection. Multiple annotators would separate these; adding a corpus now is not worth it.

**Do not go metric-hunting.** Staruch et al. (2025) work on minimal-edit GEC — read what they
report and mirror it. Thirty minutes, not a session.

---

---

## Corpus facts verified from the shipped readme (11.09) — read before S4

Four things confirmed by reading `data/raw/wi+locness/readme.txt` directly. All citable from
the corpus release itself, not inferred.

### 1. No annotation guidelines exist — confirmed, not merely unfound
The readme says only:

> **"W&I annotators have manually annotated some of these submissions and assigned them a CEFR level."**

No annotation policy, no minimal-edit instruction, no inter-annotator agreement. This is the
same sentence as the shared-task website — checked also against Yannakoudakis et al. (2018)
and the CLC annotation paper, neither of which documents it. **Cite the readme, and state
this as a limitation. Do not claim annotators were instructed to edit minimally.**

### 2. ==Gold edit spans are ERRANT-derived, not human-authored==
The readme states the M2 files were generated from **character-level** edits via ERRANT's
`json_to_m2.py`, and links a tech report on why that conversion is hard. Annotators produced
corrected *text*; the edit *spans* are algorithmic.

> **"gold edit spans are ERRANT-derived, not human-authored"**

Consequence: you cannot treat gold edit size as evidence that humans *chose* to edit
minimally. What is comparable is corrected text vs. corrected text, not edit intent.

### 3. ⚠️ TOKENISER TRAP — sanity-check this on Tuesday before debugging anything else
The M2 files were built with **spaCy v1.9.0** and **`en_core_web_sm-1.2.0`**.
`requirements.txt` pins **spaCy 3.7**. Tokenisation changed between those versions.

**When you run ERRANT to score your models, edit-span mismatches against the gold may be
tokenisation artefacts, not model behaviour.**

> **Sanity check (do this first, S4): score the gold correction against itself.
> You must get P = R = 1.0. If you don't, the problem is the tokeniser, not your code.**

Also note: v2.0 normalised all punctuation, because it was "otherwise arbitrary whether, for
example, different apostrophe styles were corrected or not." Punctuation edits are a known
noise source here.

### 4. ==Each text was annotated by a single annotator== — verified empirically
The JSON format supports multiple annotators per text and v2.1 updated the converter to
handle them, so this was worth checking. Counted directly:

> **A.dev.json — 130 texts, all with exactly 1 annotator.
> A.train.json — 1300 texts, all with exactly 1 annotator.**

So the single-annotation limitation is **confirmed, not suspected**. Write it as a verified
fact: *"each text was annotated by a single annotator."* This is why some ERRANT false
positives may be valid alternative corrections rather than overcorrections — you have no
second annotator to tell them apart.

### Bonus: fine-grained CEFR exists in the JSON but not the M2
`A.dev.json` splits as A1.i 22 · A1.ii 32 · A2.i 24 · A2.ii 52 texts.
CEFR A *is* A1+A2, so the M2 A-level file already matches the research question —
**no action needed.** Noted only in case a finer split is ever wanted.

## Session log

Fill this in at the end of every session. One or two lines. This is what makes the AI
self-declaration and the report's method section writable at the end of the month.

- **Thu 10.09** — Worked through the research-question framing (application vs.
  sentence-processing framing; considered and rejected an annotator-modelling reframing;
  returned to the original overcorrection question). Settled the three-condition design.
  Downloaded Demberg & Keller (2008) and the Fatemi (2025) thesis to `reference/`.
  Established the ERRANT conditioning structure for the metrics. *No code, no data yet.*
  *(verify/correct this entry yourself)*

---

- **Fri 12.09 – Sun 14.09** — Wrote `src/load_models.py` (MODELS config, `load()`,
  `correct_sentence()`). Smoke test passed: all three models load and generate. Had to
  downgrade transformers to 4.46.3 (v5 renamed an internal attribute that GPT-BERT's
  remote code predates) and pass `use_cache=False` for GPT-BERT. Findings: Qwen answers
  the sentence conversationally when given no instruction; both base LMs fall into greedy
  repetition loops; GPT-BERT has no `eos_token_id`, so it cannot stop on its own.

- **Mon 15.09** — Prompt design. Decided to drop the zero-shot variants from the main run
  (base LMs cannot follow instructions) and keep one zero-shot variant in the 20-sentence
  pilot only, as documented evidence. Wrote `src/select_fewshot.py`: samples few-shot
  examples from the *training* split with a fixed seed, stratified to approximate the
  corpus edit-count distribution (mean 2.12 vs pool mean 2.10) rather than demonstrating a
  constant minimal edit. Found and filtered a degenerate-reconstruction case in the corpus
  ("It . It represents ...", from a run-on split); **verified `sample.jsonl` has 0 such
  cases**. Wrote `src/prompts.py` — reads the examples from JSON so documentation cannot
  drift from what runs. Rewrote `notes/prompts.md` accordingly.
  *Still open:* GPT-BERT's `max_position_embeddings` (template is ~330 tokens).
  *Not started:* `run_pilot.py`.

## S1 · Fri 11.09 — Environment, data, frozen sample
First 20 min: fill in D1, D2, D4, D5 in `notes/decisions.md`, plus the 10-minute call on
condition 2. Then stop deliberating.

- [x] `python3 -m venv .venv && source .venv/bin/activate` — **native macOS Terminal**
- [x] `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
- [x] `curl -O https://www.cl.cam.ac.uk/research/nl/bea2019st/data/wi+locness_v2.1.bea19.tar.gz`
      → extract to `data/raw/`. Check the archive for a README with annotation notes.
- [x] `src/prepare_data.py`: parse `m2/A.dev.gold.bea19.m2` → `data/processed/sample.jsonl`
      (`id, source, gold_correction, gold_edits, n_gold_edits, n_tokens`)
- [x] Freeze **200 sentences** with ≥1 gold edit, fixed `random_state`. Commit the file.
- **Done when:** `sample.jsonl` exists, is committed, and you can print 5 rows.

### S1 outcome (11.09)
705 eligible after filtering · 200 sampled with `RANDOM_SEED = 42` · rerun verified identical.
Rejected: noop 202 · too_long 50 · punct/orth-only 46 · too_short 20 · no_effective_change 14.
Sample: mean 2.83 gold edits, mean 17.6 tokens per sentence.

**D5 settled (11.09): spelling and orthography edits are kept, everywhere.**
`KEEP_SPELL_ORTH_IN_GOLD = True`. They stay in `gold_correction` and they count as normal
edits at metric time. This follows BEA-2019 convention, where GEC includes spelling, and it
introduces no scoring bias in either direction.

Two consequences:
- **Wording:** the task is error correction in the BEA sense, which includes spelling. Either
  say "errors" rather than "grammatical errors" in the RQ, or state explicitly that spelling
  is included per shared-task convention. Do not let the two drift apart.
- **Nothing is foreclosed:** every edit's `type` is stored in `sample.jsonl`, so a
  grammar-only secondary analysis (excluding SPELL/ORTH from TP/FP) costs one filter at
  metric time if you want it. Optional, not required.

## S2 · Sat 12.09 — Three models producing output + 20-item pilot
- [x] Load all three; confirm each returns something on one sentence
- [ ] Write 2–3 prompt variants yourself → `notes/prompts.md`
- [ ] Run all variants on 20 sentences. **Read the raw output by hand.**
- ⚠️ Conditions 1 and 2 are base LMs — expect zero-shot instructions to fail; few-shot is the
      realistic route.
- **Done when:** `results/pilot_outputs.csv` + one written paragraph judging each model.

### Sun 13.09 — reserve. Use only if S1 or S2 slipped.

## S3 · Mon 14.09 — 🚦 GO/NO-GO by 10:00, then the full run
- **Path A** — pilot usable: lock the prompt, run 200 × 3 → `results/generations.jsonl`
- **Path B** — base models can't generate: switch to scoring. Per-token surprisal /
  pseudo-log-likelihood over source vs gold minimal correction vs LLM rewrite. Cheaper on
  CPU, works for all three, no decoding variance, and taps the acceptability knowledge
  BabyLMs are actually evaluated for (BLiMP) rather than a generation ability nobody claims.
- **Path C** — neither works today: email Vera Demberg, switch to proposal format.
- **Done when:** outputs exist for all 200 items in all three conditions.

## S4 · Tue 15.09 — ERRANT + metrics
Build in the order given in "Metrics and reporting structure" above. ERRANT first — it is the
load-bearing element, not one metric among several.
- **Done when:** `results/tables/metrics_per_sentence.csv` with TP/FP/FN, P/R/F0.5,
  normalised Levenshtein and lexical-difficulty columns per sentence per condition.

## S5 · Wed 16.09 — Statistics
- [ ] Three paired conditions ⇒ **Friedman test**, then post-hoc pairwise Wilcoxon with Holm
      correction. Not three uncorrected t-tests.
- [ ] Medians and effect sizes, not only p-values. Bootstrap 95% CIs.
- [ ] Sanity check: does the pattern hold on the subset where all three models fixed the error?
- **Done when:** `results/tables/stats.csv` + `notes/results-summary.md` in your own words

## S6 · Thu 17.09 — Figures, examples, repository
- [ ] 3 figures max, PDF or 300 dpi PNG
- [ ] Hand-pick 3–4 example sentences that make the contrast visible — these carry the poster
- [ ] Push to GitHub; README with install, data download, exact reproduction commands
- [ ] Update `notes/ai-use-log.md`

## S7 · Fri 18.09 — Write the 2-page summary
Single column, 11 pt, APA. Motivation + refs → RQ and hypotheses → setup → results →
discussion and limitations. Include the repo link. Full draft; do not polish.

**Limitations material already gathered:**
- Condition 1 confounds data *quantity* with data *register* (the BabyLM corpus is ~5% CHILDES,
  ~31% OpenSubtitles, ~15% Simple Wikipedia, ~56% transcribed/scripted speech overall).
- The challenge organisers themselves caution against reading BabyLMs as models of children —
  single modality, no interaction, no social scaffolding. Do not call it "a child".
- Gold M2 edits are ERRANT-derived, not human-authored spans; no W&I annotation guidelines
  are published.
- Possible GEC-corpus contamination in condition 3, but not in condition 1.
- Single annotation ⇒ some false positives are valid alternative corrections.

## S8 · Sat 19.09 — Poster
A0 portrait. Title → motivation → RQ/hypothesis → method (small pipeline diagram) → results
(3 figures) → examples → discussion, limitations, broader context. Limitations and broader
context are graded — give them real space.

## S9 · Sun 20.09 — Slack, consolidation, self-declaration draft
- [ ] Whatever slipped
- [ ] Draft the **AI self-declaration** from `notes/ai-use-log.md` while it is fresh
- [ ] Read the summary aloud; cut toward exactly 2 pages

---

## Polish week 21.–29.09
- [ ] Final cut to 2 pages · verify every reference resolves · verify the repo clones and runs
- [ ] Finalise the AI self-declaration
- [ ] Poster-date poll: https://nuudel.digitalcourage.de/d5RIr9uczEavZ1qi
- [ ] **Submit by 23:59 on 30.09**

## Rules for the remaining sessions
1. No reopening the research question. Park ideas in `notes/parked.md`.
2. Every session ends with a committed file, not a thought.
3. If a "Done when" isn't met, cut scope — don't extend the timeline.
4. Fill in the session log before closing the laptop.

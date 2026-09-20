# Results: what to report

**Not report prose.** A prioritised inventory of the numbers and the direction each one
moves, so the 2-page limit is spent on the findings that carry the argument. The
interpretation and the wording are yours.

Data: `results/pilot_outputs_qwensfamily_02_200.csv` (600 generations, 0 failures)
ERRANT: `results/errant/` · Statistics: `notes/method-record.md` §6

---

## Tier 1 — the three findings the paper stands on

### F1. Edit magnitude decreases with model size, and it is a step rather than a gradient

| Condition | median | 95% CI |
|---|---|---|
| Human annotator | 0.167 | [0.143, 0.200] |
| Qwen2.5-0.5B | 0.250 | [0.212, 0.255] |
| Qwen2.5-1.5B | 0.244 | [0.200, 0.273] |
| Qwen2.5-3B | 0.167 | [0.143, 0.200] |

Friedman chi2(2) = 17.28, p = 0.00018.
0.5B vs 1.5B **n.s.** · 0.5B vs 3B p < .001, r = .44 · 1.5B vs 3B p < .001, r = .49.
0.5B and 1.5B both differ from human (p < .001, r ~ .50); **3B vs human p_holm = 0.056**.

Report the 3B-vs-human comparison honestly: uncorrected p = .028, Holm-corrected p = .056,
i.e. **not significant after correction**. Do not write "matches the human annotator".

### F2. 3B fixes MORE real errors while making FEWER unnecessary edits

This is the finding that rules out the alternative explanation (that editing less is just
doing less). Both directions improve at once.

| | TP | FP | R | P | F0.5 |
|---|---|---|---|---|---|
| 0.5B | 117 | 888 | 0.212 | 0.116 | 0.128 |
| 1.5B | 162 | 898 | 0.293 | 0.153 | 0.169 |
| 3B | **181** | **729** | **0.327** | **0.199** | **0.216** |

TP + FN = 553 in every row (alignment check passes).
Excluding R:ORTH (see F3): F0.5 = 0.155 / 0.206 / **0.285**.

### F3. R:ORTH is a constant artefact and should be excluded

FP from R:ORTH: **245 / 247 / 273** — essentially identical across conditions, so it
carries no information about model behaviour. It is casing and token-form difference
(`what` -> `What`, `It 's` -> `It's`), i.e. output formatting, not correction behaviour.

Excluding it **widens** the effect:

| | FP with ORTH | FP without | P without |
|---|---|---|---|
| 0.5B | 888 | 643 | 0.146 |
| 1.5B | 898 | 651 | 0.192 |
| 3B | 729 | **456** | **0.276** |

3B's FP advantage over 0.5B goes from 18% to **29%**. F0.5 ratio 1.69 -> 1.84.
Give both sets of numbers and state the exclusion criterion.

---

## Tier 2 — supporting evidence (a table, or the poster)

### S1. Overcorrection is specifically unnecessary REPLACEMENT

FP by operation: R (replacement) is 83-85% of all FP in every condition
(757 / 745 / 609 out of 888 / 898 / 729). Not insertion, not deletion.

### S2. The size effect sits in the "unnecessary" categories

| Category | 0.5B | 1.5B | 3B | direction |
|---|---|---|---|---|
| OTHER (unclassifiable rewrites) FP | 249 | 247 | **163** | -34% |
| NOUN FP | 78 | 95 | 83 | flat |
| ORTH FP | 245 | 247 | 273 | flat (artefact) |
| VERB:TENSE precision | 0.44 | 0.45 | **0.69** | +57% |
| VERB:FORM precision | 0.41 | 0.47 | **0.65** | +58% |
| DET precision | 0.33 | 0.33 | **0.56** | +72% |
| PREP precision | 0.25 | 0.41 | **0.47** | +88% |

OTHER = ERRANT could not assign a type, typically multi-word paraphrase. The larger model
does a third fewer free-form rewrites while getting substantially better at canonical
grammatical categories.

### S3. Models are competent on canonical grammar, poor on lexis (3B precision)

Good: VERB:SVA .71 · VERB:TENSE .69 · VERB:FORM .65 · DET .56 · PREP .47 · WO 1.0 (3/0)
Bad: NOUN .035 (3 TP vs 83 FP) · ORTH .025 · OTHER .069 · ADV .0 · ADJ .09
(0.5B is worse still: NOUN precision **0.0** — 0 correct against 78 false)

### S4. Edit volume relative to the human annotator (excluding ORTH)

Gold: 534 edits / 200 sentences = 2.67 per sentence.
Models: 0.5B 3.77 (1.41x) · 1.5B 4.03 (1.51x) · 3B 3.15 (**1.18x**).

### S5. Direction of change

Proportion of items where the output is closer to the gold than the source was:
0.5B 18.5% · 1.5B 25.0% · 3B **37.5%**.
Items made worse: 65.0% · 56.5% · **40.0%**.
**No condition improves more often than it harms.**

### S6. Prior conditions could not do the task (pilot, n=20)

GPT-2 few-shot reproduced the input verbatim on **18/20** items; GPT-BERT continued into
invented example blocks on 19/20. Neither has an eos token.
Use this to motivate why the conditions changed — and as the concrete illustration of why
edit distance alone is insufficient (verbatim copying = zero edits = apparently perfect
minimal editing, while fixing nothing).

---

## Tier 3 — limitations that must appear

1. **Absolute performance is poor.** FP outnumbers TP 4-7x. BEA-2019 winning systems reach
   F0.5 ~0.70; these reach 0.13-0.29. The claim is about relative differences between
   conditions, not about usable correction quality.
2. **Punctuation is a blind spot for all three.** PUNCT recall .014 / .043 / .057 against
   70 gold punctuation edits, while introducing 35-47 unnecessary ones. Does not improve
   with size.
3. Post-processing (preamble removal, tokenisation) is hand-written; 1.5B most affected
   (14/200 preambles vs 3 and 1).
4. Single annotator per text; some FP may be valid alternative corrections.
5. No minimality criterion given to the models (deliberate, D6).
6. One model family, one prompt, one decoding strategy, English only, CEFR level A only.
7. Gold M2 edits are ERRANT-derived; no W&I annotation guidelines are published.

---

## Claims the data does NOT support — do not write these

- "3B matches human editing behaviour" — the median matches, but p_holm = .056, and its
  precision is 0.20. Matching magnitude is not matching behaviour.
- "Larger models are better at grammatical error correction" — too broad. One family,
  one prompt, 200 sentences, one proficiency level.
- "Smaller models overcorrect more" as a general law — 0.5B and 1.5B are statistically
  indistinguishable. The data shows a threshold somewhere between 1.5B and 3B, not a
  monotonic relationship.
- Anything about training-data size. All three models saw ~18T tokens. That variable was
  abandoned when the BabyLM conditions failed.

---

## Suggested allocation for 2 pages

- Table 1: F2 + F3 combined (TP/FP/R/P/F0.5, with and without ORTH) — the core evidence
- Figure 1: F1 (edit magnitude per condition + human reference, with CIs)
- Figure 2: S2 (OTHER FP falling vs VERB/DET precision rising) — shows where size helps
- One worked example: item A.dev.0000 (see below) — carries more than a paragraph of prose
- S5 and S6 as one or two sentences each in the text

### The example sentence (A.dev.0000)

    source : It 's difficult answer at the question " ... " if the only one who has to know it is in two minds .
    human  : It 's difficult to answer the question " ... " if the only one who has to know it is in two minds .
    3B     : It's difficult to answer the question "..." if the only one who has to know it is in two minds.
    1.5B   : It's difficult to answer the question "..." if the person who knows must be in two minds.
    0.5B   : It's challenging to answer the question "..." when the only one who knows it is unsure.

Human makes exactly two minimal edits (insert `to`, delete `at`). 3B makes the same two.
1.5B rewrites the subordinate clause. 0.5B also replaces `difficult`, `if`, and
`in two minds` — none of which contained a grammatical error.

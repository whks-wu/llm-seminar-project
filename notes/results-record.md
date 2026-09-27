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
| Qwen2.5-0.5B | 0.244 | [0.210, 0.250] |
| Qwen2.5-1.5B | 0.231 | [0.194, 0.263] |
| Qwen2.5-3B | 0.167 | [0.143, 0.194] |

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
| 0.5B | 121 | 887 | 0.219 | 0.120 | 0.132 |
| 1.5B | 163 | 900 | 0.295 | 0.153 | 0.170 |
| 3B | **181** | **724** | **0.327** | **0.200** | **0.217** |

TP + FN = 553 in every row (alignment check passes).
Excluding R:ORTH (see F3): F0.5 = 0.155 / 0.206 / **0.285**.

### F3. R:ORTH is a constant artefact and should be excluded

FP from R:ORTH: **251 / 251 / 278** — essentially identical across conditions, so it
carries no information about model behaviour. It is casing and token-form difference
(`what` -> `What`, `It 's` -> `It's`), i.e. output formatting, not correction behaviour.

---

## Tier 2 — limitations, ordered by how much they threaten the conclusion

### A. Directly limit what can be concluded — write these prominently

**A1. Absolute performance is poor; the claim is only about relative differences.**
FP outnumbers TP by 4.0-7.6x. Precision 0.12-0.28. F0.5 0.13-0.29, against ~0.70 for
BEA-2019 winning systems. The single most honest sentence available:
**no condition improves more items than it harms** (improved 18.5% / 25.0% / 37.5%;
made worse 65.0% / 56.5% / 40.0%).
Without this, readers will take the result to mean 3B is usable for correction. It is not.

**A2. The 3B-vs-human comparison is not significant.**
Uncorrected p = .028; **Holm-corrected p = .056**. The medians coincide (0.167 vs 0.167),
which invites the phrase "matches the human annotator" — the statistics do not support it,
and 3B's precision is only 0.199. **Equal edit magnitude is not equal edit behaviour.**

**A3. Post-processing is hand-written, and its effect is asymmetric across conditions.**
Preamble removal and tokenisation normalisation are heuristics, not standard tools. Crucially
the preamble rate differs by condition: **1.5B 14/200, 0.5B 3/200, 3B 1/200.** How cleanly
the rule strips affects 1.5B far more than the others — a potential systematic bias that
must be declared rather than discovered by a reader.

**A4. The pilot evidence is n = 20.**
The claim that developmentally-plausible-scale models cannot perform generative correction
rests on 20 sentences. 18/20 verbatim copying is a strong signal, but it is still n = 20.

### B. Properties of the data — short but required

**B1. Single annotator per text.** Verified directly: A.dev 130/130 and A.train 1300/1300
texts have exactly one annotator. Some false positives may be valid alternative corrections
rather than overcorrection, and there is no second annotation to tell them apart.

**B2. No published annotation guidelines.** Checked the shared-task page, Yannakoudakis
et al. (2018), the CLC annotation paper, and the corpus readme. W&I+LOCNESS is
*conventionally* treated as a minimal-edit corpus, but no annotation standard backs that,
and the data contains counter-examples (one `R:WO` edit reorders seven tokens at once).

**B3. Gold edit spans are ERRANT-derived, not human-authored.** Annotators produced
corrected *text*; the spans were extracted algorithmically. Gold edit magnitude therefore
cannot be used as evidence that annotators chose to edit minimally.

**B4. Excluding R:ORTH is a judgement call.** Both sets of numbers are reported, but the
decision that orthographic normalisation "is not correction behaviour" can be contested.

### C. Costs of deliberate design choices

**C1. No minimality criterion was given to the models** (D6). Instructing minimal editing
would have measured instruction-following rather than intrinsic tendency, but the cost is
that some observed variation may reflect differing default interpretations of how much to
change, not differing restraint.

**C2. One prompt, one decoding strategy.** Greedy decoding only; prompt sensitivity untested.
A single prompt formulation was used for the 200-item run.

### D. Generalisation

**D1.** One model family (Qwen2.5), English only, CEFR level A only, n = 200, single
proficiency level. Nothing here establishes that the pattern holds across families — the
same-family design was chosen precisely to avoid confounding family with size, which means
cross-family generalisation is explicitly out of scope.

### E. Both a finding and a limitation

**E1. Punctuation is a blind spot for all three models and does not improve with size.**
Recall .014 / .043 / .057 against 70 gold punctuation edits, while introducing 35-47
unnecessary ones. This shows the size effect is **not uniform across error types** — which
qualifies any general claim that larger models correct better.

---

## Which figures and tables must be described

Two pages will not hold everything. Three items are non-negotiable; each needs at least one
sentence in the running text saying what it shows and why it matters — a figure left to
speak for itself does not satisfy "are the results presented clearly".

**Table 1 (essential): ERRANT TP / FP / R / P / F0.5, with and without R:ORTH.**
The core evidence. It is the only element that reports *both* how much was fixed and how
much was needlessly changed, and therefore the only thing that rules out "editing less is
just doing less".

**Figure 1 (essential): edit magnitude per condition with the human reference.**
Medians with bootstrap CIs, plus Friedman chi2(2) = 17.28, p = .00018 and the post-hoc
outcome. Mark the 3B-vs-human comparison as n.s.

**Example A.dev.0000 (essential).** Not a figure, but more effective than one. Human makes
two minimal edits; 3B makes exactly the same two; 1.5B rewrites the subordinate clause;
0.5B additionally replaces `difficult`, `if` and `in two minds`, none of which contained a
grammatical error.

**Figure 2 (if space allows): OTHER false positives falling (249 -> 247 -> 163) against
VERB:TENSE precision rising (.44 -> .45 -> .69).** Shows *where* scale helps — fewer
free-form rewrites, better canonical grammar — which is a level deeper than "smaller edits".

**Pilot failure: two sentences of text, no table needed.** GPT-2 reproduced the input on
18/20 items; GPT-BERT continued into invented example blocks on 19/20.

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

### The example sentence (A.dev.0000)

    source : It 's difficult answer at the question " ... " if the only one who has to know it is in two minds .
    human  : It 's difficult to answer the question " ... " if the only one who has to know it is in two minds .
    3B     : It's difficult to answer the question "..." if the only one who has to know it is in two minds.
    1.5B   : It's difficult to answer the question "..." if the person who knows must be in two minds.
    0.5B   : It's challenging to answer the question "..." when the only one who knows it is unsure.

Human makes exactly two minimal edits (insert `to`, delete `at`). 3B makes the same two.
1.5B rewrites the subordinate clause. 0.5B also replaces `difficult`, `if`, and
`in two minds` — none of which contained a grammatical error.

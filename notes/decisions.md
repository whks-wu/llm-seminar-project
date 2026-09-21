# How the project changed: from BabyLM to small locally deployable models

*This note explains why I shifted the focus of my project from BabyLM to small-parameter
models that can be deployed locally.*

## Starting point

My project proposal originally planned to investigate whether **models trained on small
datasets exhibit less overcorrection**.

My motivation stems from the fact that BabyLM models are low-cost for both individuals and
institutions: they can be deployed locally and do not require renting supercomputers or
buying access to large models or APIs from major AI companies. This makes them more
conducive to educational equity — any individual or institution with a personal computer
and internet access could use language models to support language education.

During the experiment, I realised I could also investigate whether **the number of
parameters** affects overcorrection when models correct grammatical errors.

---

## 1st adjustment: there are two dimensions to BabyLM's "small"

After rereading the BabyLM Challenge materials, I realised that BabyLM models do not only
have a smaller training dataset. Of the training corpus:

- about **5%** is CHILDES child-directed speech,
- **31%** is movie subtitles,
- **15%** is Simple Wikipedia,

so the cognitive difficulty of the corpus is relatively low. In addition to having a far
smaller training dataset than large language models, BabyLM's training data is also
cognitively simpler.

In other words, BabyLM and Qwen differ in **all** dimensions (data volume, number of
parameters, instruction tuning, architecture), so any differences in the results could not
be attributed to any single one of these factors.

**Decision:** I introduced GPT-2 as a transitional condition and set up three pairwise
comparisons:

| Comparison |
|---|
| GPT-BERT vs. Qwen2.5-3B |
| GPT-2 vs. GPT-BERT |
| GPT-2 vs. Qwen2.5-3B |

---

## 2nd adjustment: the two base LMs cannot handle this task

After coding the experimental pipeline, I tested zero-shot and few-shot prompting on a
small sample of 20 sentences:

- **GPT-2** directly copied the input in **18 of 20** cases.
- **GPT-BERT** continued the text in **19 of 20** cases, and its output was only
  **0.66×** the length of the original sentence.
- GPT-BERT has **no EOS token** (its `eos_token_id` is `None`), and neither model stopped
  on its own.

This indicates that the non-instruction-tuned models tested here — base LMs — are unable to
perform this grammatical error correction task.

**Decision:** I abandoned BabyLM and GPT-2 and switched to **Qwen2.5 0.5B, 1.5B and 3B**.
I chose models from the same family, because mixing families would conflate *family* with
*scale*.

**Critical consequence:** all three new models were trained on ~18T tokens, so **the
independent variable shifted from the amount of training data to the number of
parameters**. The research question had to be rewritten.

---

## 3rd adjustment: few-shot prompting fails for instruction-tuned models

After switching models, I ran a second 20-sentence test, again with zero-shot and few-shot
prompts. Under **few-shot**:

| Model | Outputs with a preamble | Median edit distance (raw, 20-item pilot) |
|---|---|---|
| Qwen2.5-0.5B | 7 / 20 | 0.858 — highest of the six conditions |
| Qwen2.5-1.5B | 0 / 20 | 0.393 — lowest of the six conditions |

Qwen2.5-0.5B also sometimes interpreted the eight few-shot examples as a dialogue
transcript and replied with an apology.

**Decision:** use only zero-shot prompts for the instruction-tuned models — although
zero-shot outputs were contaminated by preambles such as *"The corrected sentence is:"*.

---

## 4th adjustment: prompt iteration

I modified the prompt to explicitly require *output only the corrected sentence*.

| | Responses with a preamble |
|---|---|
| Before the change | ~23 / 60 |
| After the change | 1 / 60 |

---

## Why the metrics became more complex step by step

1. **Starting assumption.** I first thought that with Levenshtein edit distance, fewer
   changes meant less overcorrection.

2. **Spelling edits are kept.** If spelling edits were excluded from the gold data, Qwen's
   correct spelling corrections would be counted as overcorrections, systematically biasing
   the result toward the hypothesis. Therefore all spelling edits were retained.

3. **Fewer changes ≠ restraint.** GPT-2 copied the input in 18 of 20 cases, giving an edit
   distance of 0. On a naive metric this looks like a *perfect minimal modification*, but it
   did not correct a single error. **"Fewer changes" cannot distinguish restraint from
   incompetence.**

4. **ERRANT recall as a gate.** To determine whether a model actually made the right
   corrections, I used ERRANT and computed recall from its output.

5. **Tokenisation.** The corpus is pre-tokenised (`It 's`), while model output is natural
   text (`It's`). On the same 200 sentences, the median edit distance was **0.375–0.438
   before normalisation and 0.167–0.250 after** — i.e. **43–56%** of the raw distance was
   tokenisation noise.

6. **Regenerated reference.** The M2 file shipped with the corpus was generated with
   spaCy 1.9 and should not serve as the reference for a modern ERRANT (spaCy 3.x).
   I therefore regenerated `ref.m2` from the (source, gold) pairs using the same ERRANT
   installation as for the model outputs.

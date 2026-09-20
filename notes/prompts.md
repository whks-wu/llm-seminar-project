# Prompt design

**Single source of truth for the actual strings: `src/prompts.py`.**
The few-shot examples themselves live in `notes/fewshot_examples.json` and are read at
import time — they are deliberately NOT duplicated here, so this file cannot drift out of
sync with what actually ran. To see the exact prompt the models receive:

```bash
python3 src/prompts.py
```

---

## Variant 1 — zero-shot-01

```
Correct the grammatical errors in this sentence.

{sentence}
```

`stop = None` (no truncation). Qwen typically answers with a preamble ("Here is the
corrected sentence: ..."), so truncating at the first newline would cut off the answer
rather than the noise. Raw output is kept and read by hand.

**Used in the 20-sentence pilot only, not in the 200-sentence main run.**

*Why it exists:* it was written before the smoke test, when I did not yet know that
GPT-BERT and GPT-2 are not instruction-tuned. Running it once on 20 sentences turns
"base LMs cannot follow zero-shot instructions" from an assumption into a documented
observation I can cite in the report. Running it on all 200 would be wasted compute.

## Variant 2 — few-shot

8 demonstration blocks, then the item to be corrected:

```
Original: <source>
Corrected: <gold>

... x8 ...

Original: {sentence}
Corrected:
```

`stop = "\n"`. Base LMs have no EOS token (GPT-BERT's `eos_token_id` is `None`), so they
cannot signal completion and will always run to `max_new_tokens`. The blank-line block
structure makes the first newline the only available stop signal.

Template length: ~1325 characters, roughly 330 tokens, before the test sentence is inserted.

### How the examples were chosen

`src/select_fewshot.py`, fixed seed 42, drawn from the **training** split
(`A.train.gold.bea19.m2`) — disjoint from `A.dev`, which the evaluation sample comes from.
Examples must never overlap the test items.

Filters: 8–18 tokens; 1–4 edits; no UNK edits; not punctuation/orthography-only; rejects
reconstructions that come out as broken English (a few W&I annotations split a run-on by
inserting ". X", which on an already-segmented sentence produces "It . It represents ...").

Stratified quota {1 edit: 3, 2: 2, 3: 2, 4: 1} → mean **2.12** edits per example, against a
pool mean of **2.10** for the same 8–18 token band.

**Why stratified rather than hand-picked:** few-shot examples implicitly demonstrate *how
much* to edit. An all-minimal example set would nudge every model toward minimal editing
and could flatten the very difference the study is trying to measure. Sampling to
approximate the corpus edit-count distribution makes that bias explicit, documented and
reproducible instead of arbitrary.

Note: `sample.jsonl` averages 2.83 edits, but it spans 5–40 tokens; longer sentences carry
more errors, so 2.83 is not the right reference for 8–18 token examples.

---

## Open decisions

- [ ] No instruction line precedes the few-shot examples. Keep it that way, or add one?
      (An ambiguous instruction after 8 demonstrations may be noise rather than help.)
- [ ] Whether the example set needs a different seed after reading all 8 by hand.
- [ ] GPT-BERT's `max_position_embeddings` is still unchecked. If it is 512, a ~330-token
      prompt leaves ~150 tokens for generation; if 256, the prompt overflows and the
      example count must be cut.

## Limitations to carry into the report

- All three models receive the identical prompt, so prompt effects are constant across
  conditions — but the few-shot examples still impose a shared edit-size prior on all of them.
- Two of the eight examples begin with a punctuation edit (`M:PUNCT`), so the prompt does
  demonstrate that punctuation is in scope. Consistent with D5 (punctuation edits retained),
  but worth stating.


## updated Variant 1 — zero-shot-02

```
Correct only grammatical errors in this sentence and then only output the corrected sentence.

{sentence}
```
*Why updated:* The outputs are not clear and don't keep simple. They have explanation. 
Examples:
Half of them have a preface, half do not, and the format of the prefaces is inconsistent.

without preface，one line sentence:
I believe that the public transportation will always be in the future.

Colon + line break + quotation marks:
The corrected version of the sentence would be:\n\n"It's difficult to..."

Colon + quotation marks, on the same line:
The corrected sentence is: "I think that public transport will..."

Colon + line break, no quotes:
Here is the corrected version of the sentence:\n\nAlso, you'll meet...

Two Lines of Introduction + Comments:
The sentence is almost correct, but it can be improved for clarity and grammatical correctness. Here's a revised version:\n\n"..."

*Possible Issues:* Because of two instances of “only” in a single sentence, referring to different objects, A small model like 0.5B might interpret the two “only”s as a single concept.
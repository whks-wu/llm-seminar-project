# Design decisions (my own — record reasoning, not just the choice)

## D1. Size-matched control condition?
Decision: BabyLM vs GPT-2-small; GPT-2-small vs Qwen; BabyLM vs Qwen
Reasoning: 

## D3. BabyLM checkpoint chosen, and why
BabyLM is called BabyLM not only because it was trained on a relatively small dataset, but also because the content of that dataset is child-directed.
So I should in fact choose a LM with small training datasize. BabyLM is a LM with lower cognitive complexity. If I still want to compare it with LLM the
research question is changed or should be cover bigger, it should be like "a LM with lower cognitive complexity or a LM trained on small dataset versus LLM which one shows lower trend on 
grammar overcorrection "
Decision: BabyLM vs GPT-2-small; GPT-2-small vs Qwen; BabyLM vs Qwen
"You already have human behavioural data and may not have noticed: the gold edits in A.dev.gold.bea19.m2 are corrections produced by human annotators, with an explicit minimal-edit annotation policy. What does having a human baseline let you ask that "which model scores better" doesn't?" 
I can treat the corrections produced by human annotators as human baseline and it will be used to compare with the corrections by models. 
Reasoning: Only in this way I then match the topic which is discussed in this semeniar. 

## D4. LLM control chosen, and why
Decision:
Reasoning:

## D5. Sample: which CEFR level, how many sentences, filtering rules
Decision (as implemented in `src/prepare_data.py`, settled 11.09):
- CEFR level A (= A1 + A2) dev split, `A.dev.gold.bea19.m2`
- 200 sentences, `RANDOM_SEED = 42`, frozen and reproducible via `sample_manifest.json`
- Length band 5-40 tokens
- Punctuation/orthography-only sentences dropped
- Spelling and orthography edits KEPT everywhere (in gold and in metrics), per BEA-2019
  convention; removing them from gold would bias results toward the hypothesis
- UNK edits kept; 14 degenerate items where the recorded correction equals the source dropped
- Result: 1037 -> 705 eligible -> 200 sampled

Reasoning: (write this yourself — the decisions above are recorded, the justification is
what the report needs and what the grading criteria assess)

## D6. Prompting strategy (settled 15.09)
Decision:
- Few-shot only for the 200-sentence main run; one zero-shot variant in the 20-sentence
  pilot as documented evidence that base LMs do not follow instructions
- All three models receive the identical prompt
- 8 demonstration examples, sampled from the TRAINING split with seed 42, stratified to
  approximate the corpus edit-count distribution
- No explicit "minimal edit" instruction in any prompt

Reasoning: 



---

# REVISION 16.09 — conditions changed after the pilot

## D7. Why the BabyLM / GPT-2 conditions were dropped

Evidence: `results/pilot_outputs.csv`, 20 sentences x 3 models x 2 prompt variants.

- GPT-2, few-shot: 18/20 outputs identical to the input. It learned the output *format*
  from the demonstrations but not the correction task.
- GPT-BERT, few-shot: 19/20 continued into newly invented example blocks; outputs are
  fragments (median length 0.66x the source).
- Both, zero-shot: open-ended continuation, 1.65-1.80x source length.
- Neither has an eos token, so neither can stop on its own.

Two of three conditions therefore never produce a correction. An overcorrection comparison
is impossible when two arms do not correct at all.

**Methodological point worth keeping:** verbatim copying scores zero edit distance, i.e.
*perfect* minimal editing on a naive Levenshtein metric, while fixing nothing. The ERRANT
recall gate is what separates restraint from incapacity — this pilot is the empirical
justification for it.

## D8. Replacement conditions: Qwen2.5 size ladder

0.5B / 1.5B / 3B-Instruct. Same family: pretraining corpus, instruction tuning,
architecture and tokenizer all constant; only parameter count varies.

Chosen over a mixed-family set (SmolLM2 / Llama-3.2 / Qwen) because a mixed set confounds
family with size. Generalisation across families belongs in the discussion, not in the design.

Reasoning: (write this yourself)

## D9. THE RESEARCH QUESTION HAS CHANGED — rewrite it

All three replacement models are pretrained on ~18T tokens. **The independent variable is
now parameter count, not training-data size.** The original question — whether models
trained on little data overcorrect less — cannot be answered with these conditions.

The new question has to be about model *size* among locally deployable free models, which
is the practical motivation stated in the original project draft ("faster response and
lower computational costs, or even no cost at all").

New research question (Among models that learners can deploy locally for free, does model size affect the tendency toward overcorrection? — this is the one thing that must be entirely your own,
and it is what the "is the research question well-motivated / appropriately specific"
criterion assesses):

Reasoning:

## D10. Narrative for the report

The BabyLM reading is not wasted — it becomes the motivation *and* the first result:

1. Motivation: BabyLM literature, minimal-edit pedagogy, low-cost educational AI.
2. Result 1: models at developmentally plausible pretraining scale cannot do generative
   error correction at all (pilot table).
3. Therefore: turn to the class of models a learner could actually deploy for free.
4. Result 2: the size comparison.

This makes the model swap a data-driven design decision rather than a change of topic.

## D11. Disable few-shot

Reasoning: Because when using few-shot prompt techniques with command-based models, the model may respond based on its understanding of these examples—it may output the corrected sentence directly, or it may provide an explanatory statement followed by the corrected sentence.
And hallucinations may also occur. (Qwen2.5-0.5B and Qwen2.5-3B)

Surprisingly, the sentences generated by Qwen2.5-1.5B are very straightforward and follow the prompt exactly.

But there is a output under zero-shot "The corrected sentence is:

"I think that the public transport will always be in the future."" which has a preface.
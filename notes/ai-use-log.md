# AI use log
One line per session. This is the raw material for the self-declaration due 30.09.
Record: date | what was AI-assisted | what was entirely mine.

- 2026-09-07 | Assistant: read the two PDFs, located the W&I+LOCNESS download URL and the
  CEFR-A m2 file, verified BabyLM model IDs on HuggingFace, drafted this repo skeleton and
  the session schedule in PLAN.md (project management, not project content).
  Mine: research question, hypotheses, metric design — all unchanged from my own project draft.

- 2026-09-10 | Assistant: verified the BabyLM corpus composition and the organisers' caveats
  against reading BabyLMs as child models; verified that no W&I annotation guidelines are
  published (checked the shared-task page, Yannakoudakis et al. 2018, and the CLC annotation
  paper) and corrected an earlier wrong claim of mine about a minimal-edit policy; confirmed
  BEA-2019's official metric is ERRANT span-based F0.5; located matched-data BabyLM
  checkpoints; explained the distinction between applied and sentence-processing framings and
  pointed to Demberg & Keller (2008); flagged the incapacity-vs-restraint confound in the
  edit-distance metric and the need for a recall gate; rewrote PLAN.md (schedule and
  reporting structure).
  Mine: the research question and the decision to keep it after considering a reframing; the
  three-condition design; all interpretation. I declined the assistant's suggested reframing
  on the basis of my supervisor's own feedback on my draft.
  NOTE TO SELF: review this entry honestly before writing the self-declaration. If unsure
  whether any of the above exceeds what the course permits, ask Vera Demberg by email.

- 2026-09-11 | Assistant: read the corpus readme with me and confirmed no annotation
  guidelines are shipped; counted annotators per text (all A-level texts have exactly one);
  produced the error-type distribution I used to make the D5 filtering decisions; flagged
  that excluding SPELL/ORTH edits from the gold reference would bias results toward my
  hypothesis, and I accepted the alternative (keep them in gold, exclude at metric time);
  WROTE src/prepare_data.py (M2 parsing, edit reconstruction, filtering, sampling) and
  debugged it, including spotting 14 degenerate UNK annotations where the recorded
  correction equals the source.
  Mine: all four D5 filtering decisions (punctuation-only, spelling, length band, UNK);
  the research question and design.
  NOTE: src/prepare_data.py was substantially AI-written. This MUST be stated specifically
  in the self-declaration — the course permits AI for programming but requires it be
  documented clearly and kept to a minimum.

- 2026-09-15 | Assistant: debugged `src/load_models.py` over 12-14.09 (diagnosed the
  transformers v5 vs GPT-BERT remote-code incompatibility, the `use_cache` assertion, the
  `time.time` missing-parens bug, and that warnings fire at load time not generate time);
  explained M2 edit application, `**kwargs`, `json.load` vs `loads`, f-string placeholder
  evaluation, and `str.join` semantics; extracted candidate few-shot examples from
  A.train and WROTE `src/select_fewshot.py`; found the degenerate-reconstruction case and
  verified sample.jsonl is clean; reviewed and corrected `src/prompts.py` (I wrote the
  code, the assistant found bugs); rewrote `notes/prompts.md` and updated PLAN/decisions.
  Mine: all prompt content and wording; the 8 filtering/design decisions (D5, D6); the
  decision to drop zero-shot from the main run; `src/load_models.py` and `src/prompts.py`
  were written by me with the assistant reviewing.
  NOTE: `prepare_data.py` and `select_fewshot.py` are substantially assistant-written;
  `load_models.py` and `prompts.py` are mine with assistant debugging. State this split
  specifically in the self-declaration.

- 2026-09-16 | Assistant: continued debugging `src/load_models.py` (diagnosed `AutoModel`
  having no `.generate()`, `.eval(device)`, `df[0]` vs `df.iloc[0]`, the missing
  `if __name__ == "__main__"` guard, and a wrong `import ... as pd`); explained why ERRANT
  is needed at all (that edit distance alone cannot distinguish a model that edits little
  because it is restrained from one that edits little because it cannot correct - the
  incapacity-vs-restraint confound - so a recall gate is required); estimated remaining
  work.
  Mine: all code decisions; I set my own schedule and told the assistant to stop pacing me.

- 2026-09-17 .. 2026-09-19 | Assistant: debugged `src/run_pilot.py`, which I wrote
  (found that the `unlink` call sat inside the loop and was destroying the previous
  models' rows, and a second `time.time` missing-parens bug); updated the condition table
  in `notes/PLAN.md` and `notes/decisions.md` after I changed the design; updated the
  `MODELS` dict to the Qwen2.5 ladder.
  Mine: reading the 20-sentence pilot output and concluding that GPT-2 (verbatim copying,
  18/20) and GPT-BERT (fragments, 19/20) cannot perform generative GEC; the decision to
  replace them with a single-family parameter ladder (Qwen2.5-0.5B / 1.5B / 3B-Instruct)
  and to drop GPT-2 entirely; the decision to drop few-shot and use zero-shot only, which
  I made by reading the few-shot outputs myself; the final prompt wording.

- 2026-09-20 | Assistant: set up ERRANT (diagnosed the numpy 1.x/2.x ABI break and that I
  had installed into the wrong venv; built `.venv-errant` with `numpy<2` first; fixed the
  `en_core_web_sm` download); WROTE `src/export_for_errant.py`; identified that the M2 file
  shipped with the corpus was produced with spaCy 1.9 and must NOT be used as the ERRANT
  reference, and that regenerating `ref.m2` with the same ERRANT removes 43-56% of the
  measured edit volume as pure tokenisation noise; wrote the `.gitignore` rules that keep
  corpus text and derivatives out of the public repo (W&I+LOCNESS licence clause 6 allows
  publishing only excerpts under 100 words).
  Mine: the decision to use ERRANT F0.5 as the official metric; the decision not to push
  any corpus-derived file.
  NOTE: `src/export_for_errant.py` is substantially assistant-written. Add it to the list
  with `prepare_data.py` and `select_fewshot.py` in the self-declaration.

- 2026-09-22 | Assistant: reformatted `notes/decisions.md`, which I wrote, into markdown
  and corrected two factual errors in it that were the assistant's own from earlier
  sessions; proofread a draft of the 2-page summary (31 tracked changes, 6 comments -
  grammar, terminology consistency, and factual checks against `results-record.md`);
  explained findings F1/F2/F3 and the full limitations inventory to me in Chinese when I
  asked what the numbers meant.
  Mine: the whole text of `notes/decisions.md`; the whole draft of the 2-page summary.

- 2026-09-23 | Assistant, on the 2-page summary: proofread it (grammar, agreement,
  a dangling participle, singular/plural consistency for "annotator"); FACT-CHECKED it
  against my own records and found (i) a table column headed "Difference (with-without
  ORTH)" whose values were actually the R:ORTH false-positive counts, (ii) an F0.5 range
  that mixed the with-ORTH and without-ORTH columns, (iii) a prompt string in the text that
  did not match `src/prompts.py`; explained that ERRANT TP/FP/FN count edit spans, not
  sentences (hence 888 FP over 200 items), and derived per-sentence edit rates
  (5.03 / 5.30 / 4.55 for the models vs 2.77 for the annotator); reverse-engineered from my
  precision figures that excluding R:ORTH also removes 7 true positives per condition;
  MARKED WHICH PASSAGES WERE REDUNDANT AND COULD BE CUT and applied 13 deletions as tracked
  changes for me to accept or reject one by one (1179 -> 947 words) - deletions only, no
  rewriting and no new sentences; pointed out that two items I had put under "Limitations"
  were results, not limitations, and belonged in the Results section.
  Assistant, on the references: FOUND the two sources I was missing (the ERRANT paper,
  Bryant et al. 2017; and the source of the BEA-2019 winning F0.5, Bryant et al. 2019,
  Table 7), and established that the actual figure is 69.47 on the blind test set across
  all CEFR levels, which is not comparable to my CEFR-A dev subsample; extracted
  bibliographic metadata from the three PDFs in `reference/`; formatted 8 references in APA;
  inserted 7 in-text citations as tracked changes; set the hanging indent and font size.
  Mine: every sentence of the 2-page summary is my own writing. I decided each cut
  (accept/reject), decided to remove the Limitations section after re-reading the
  requirement, decided to delete the BEA-2019 comparison rather than qualify it, and
  decided which references to include and which to leave out.
  NOTE: the assistant's work on the summary was proofreading, fact-checking against my own
  records, formatting, and reference work. It also judged which of my passages were
  redundant - that is editorial, not authorial, but state it plainly rather than calling it
  "grammar checking".

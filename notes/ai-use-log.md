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

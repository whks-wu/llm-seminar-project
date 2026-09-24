# Overcorrection in LLMs with different number of parameters grammatical error correction

Final project — *LLMs as models of human sentence processing*, SoSe26, Universität des Saarlandes.
Author: Qiancao Jiang

## Research question
Does the number of parameters in locally deployable, open-source, and free large language models affect the phenomenon of overcorrection when the models correct grammatical errors?

## Setup

Two environments are needed. They are kept separate on purpose: ERRANT is built
against the numpy 1.x C ABI and cannot share an environment with the numpy 2.x
that the rest of the pipeline uses.

**Main environment** — generation, measurement, statistics:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**ERRANT environment** — scoring only. Install numpy first, or the import fails
with `ValueError: numpy.dtype size changed`:

```bash
python3 -m venv .venv-errant
source .venv-errant/bin/activate
pip install -r requirements-errant.txt
python -m spacy download en_core_web_sm
deactivate
```

Exact package versions used for the reported results are recorded in
`results/tables/env.txt`.

## Data
W&I+LOCNESS v2.1 (BEA-2019 shared task). Not redistributed here — download it yourself:
```bash
curl -O https://www.cl.cam.ac.uk/research/nl/bea2019st/data/wi+locness_v2.1.bea19.tar.gz
tar -xzf wi+locness_v2.1.bea19.tar.gz -C data/raw/
```
Licence: non-commercial research and educational use only. Attribution required:

> Helen Yannakoudakis, Øistein E. Andersen, Ardeshir Geranpayeh, Ted Briscoe and Diane
> Nicholls. 2018. Developing an automated writing placement system for ESL learners.
> *Applied Measurement in Education*, 31(3), 251–267.

**The corpus text is not redistributed in this repository.** The W&I licence (clause 6)
permits publishing excerpts of fewer than 100 words only, and the stimulus set contains
roughly 3,500. `data/processed/sample.jsonl` is therefore git-ignored.

To reproduce the exact stimulus set: download the corpus as above, then run

```bash
python src/prepare_data.py
```

`data/processed/sample_manifest.json` is committed and records the random seed, every
filter setting, the 200 item ids and a SHA-256 of the generated file. Compare the printed
checksum against the manifest to confirm you have regenerated an identical sample.

## How to run 
prepare_data.py → run_pilot.py → compute_magnitude.py → statistic_analyse.py
                                → export_for_errant.py → (errant venv) errant_parallel/compare


## Reproducing the results

Six steps. Steps 1–2 need the corpus and the models; steps 3–6 run from files
that are already in the repository, so the tables can be regenerated without
re-running generation.

```bash
source .venv/bin/activate

# 1. Build the stimulus set from the corpus (see "Data" above for the download).
#    -> data/processed/sample.jsonl  +  sample_manifest.json
python src/prepare_data.py

# 2. Generate. Downloads ~8 GB of Qwen2.5 weights on first run and takes about
#    20 minutes on Apple Silicon (MPS). Greedy decoding, so the output is
#    deterministic.
#    -> results/pilot_outputs_qwensfamily_02_200.csv
python src/run_pilot.py

# 3. Edit magnitude. Reads the generations and notes/preamble_suffix_manual.csv,
#    the manual annotation of model commentary (28 rows, committed).
#    -> results/tables/edit_magnitude.csv          [200 items x 4 conditions]
python src/compute_magnitude.py

# 4. Statistics on that table.
#    -> results/tables/medians.csv    [Table 1]
#    -> results/tables/friedman.csv   [Finding 1]
#    -> results/tables/stats.csv      [Finding 1, pairwise]
#    -> results/tables/env.txt        [versions and test settings]
python src/statistic_analyse.py

# 5. Write the parallel plain-text files ERRANT needs. Uses the same cleaning
#    function as step 3, so both measures see identical model output.
#    -> results/errant/source.txt, gold.txt, hyp_<model>.txt
python src/export_for_errant.py
deactivate
```

```bash
# 6. Score with ERRANT, in its own environment.
source .venv-errant/bin/activate
cd results/errant

errant_parallel -orig source.txt -cor gold.txt -out ref.m2
for m in Qwen2.5-0.5B Qwen2.5-1.5B Qwen2.5-3B; do
  errant_parallel -orig source.txt -cor "hyp_$m.txt" -out "hyp_${m#Qwen2.5-}.m2"
done
for s in 0.5B 1.5B 3B; do
  errant_compare -hyp "hyp_$s.m2" -ref ref.m2        > "../tables/errant_${s}_overall.txt"
  errant_compare -hyp "hyp_$s.m2" -ref ref.m2 -cat 1 > "../tables/errant_${s}_cat1.txt"
  errant_compare -hyp "hyp_$s.m2" -ref ref.m2 -cat 2 > "../tables/errant_${s}_cat2.txt"
done
cd ../..
deactivate
```

`errant_*_overall.txt` gives Table 2; `errant_*_cat2.txt` gives the ORTH counts
in Finding 3. Step 6 regenerates `ref.m2` from (source, gold) with the same
ERRANT that scores the hypotheses — see `src/export_for_errant.py` for why the
M2 shipped with the corpus is not used.

Everything in `results/tables/` is plain numbers and is committed, so the
reported values can be checked without running anything.

## AI use
See the self-declaration submitted with the report.

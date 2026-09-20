# Overcorrection in BabyLM vs. LLM grammatical error correction

Final project — *LLMs as models of human sentence processing*, SoSe26, Universität des Saarlandes.
Author: Qiancao Jiang

**Status: in progress.** See `PLAN.md` for the working schedule.

## Research question
(to be written)

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

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

## Reproducing the results
(to be written — exact commands for each table and figure)

## AI use
See the self-declaration submitted with the report; running log in `notes/ai-use-log.md`.

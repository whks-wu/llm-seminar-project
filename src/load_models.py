import pandas as pd
import torch
from pathlib import Path
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
import warnings
warnings.filterwarnings("ignore", message=".*do_sample.*")

# Three conditions on one ordered scale of PARAMETER COUNT. Same family, so pretraining
# data, instruction tuning, architecture and tokenizer are held constant and only size
# varies.
MODELS = {
    "Qwen2.5-0.5B": {
        "model_id": "Qwen/Qwen2.5-0.5B-Instruct",
        "auto_class": AutoModelForCausalLM,
        "is_chat": True,
        "load_kwargs": {
            "trust_remote_code": True,
            "torch_dtype": "auto",
            "local_files_only": True,
        },
        "generate_kwargs": {},
    },
    "Qwen2.5-1.5B": {
        "model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "auto_class": AutoModelForCausalLM,
        "is_chat": True,
        "load_kwargs": {
            "trust_remote_code": True,
            "torch_dtype": "auto",
            "local_files_only": True,
        },
        "generate_kwargs": {},
    },
    "Qwen2.5-3B": {
        "model_id": "Qwen/Qwen2.5-3B-Instruct",
        "auto_class": AutoModelForCausalLM,
        "is_chat": True,
        "load_kwargs": {
            "trust_remote_code": True,
            "torch_dtype": "auto",
            "local_files_only": True,
        },
        "generate_kwargs": {},
    },
}

# Dropped after the 20-sentence pilot (results/pilot_outputs.csv), kept here for the record:
#   "gpt-bert-babylm-small" -> ltg/gpt-bert-babylm-small  (10M words, ~30M params)
#   "gpt2"                  -> openai-community/gpt2      (~9B tokens, 124M params)
# Neither can perform generative error correction: GPT-2 reproduced the input verbatim on
# 18/20 few-shot items, GPT-BERT emitted fragments and continued into new example blocks
# on 19/20. Both also lack an eos token, so they cannot stop. The pilot output is retained
# as Table 1 evidence rather than re-run at n=200.

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data/processed/sample.jsonl"

if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("use Mac GPU(MPS)")
else:
    device = torch.device("cpu")
    print("use CPU")

def load(model_name):
    config = MODELS[model_name]

    model_id = config["model_id"]
    ModelClass = config["auto_class"]
    load_kwargs = config["load_kwargs"]

    tokenizer = AutoTokenizer.from_pretrained(model_id, **load_kwargs)
    model = ModelClass.from_pretrained(model_id, **load_kwargs).to(device).eval()

    model.generation_config.temperature = None

    return tokenizer, model

def correct_sentence(tokenizer, model, text, is_chat, generate_kwargs, max_new_tokens=128):
    """Return the model's raw, unprocessed output."""
    if is_chat:
        prompt = tokenizer.apply_chat_template([{"role":"user", "content":text}], tokenize=False, add_generation_prompt=True)
    else:
        prompt = text
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, **generate_kwargs, temperature=None, top_p=None, top_k=None)
    new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)

def main():
    df = pd.read_json(SAMPLE_PATH, lines=True)
    text = df.iloc[0]["source"]
    for name in MODELS:
        start_load = time.time()
        tok, m = load(name)
        end_load = time.time()
        print(f"Total runtime of load() is {end_load - start_load:.1f} s")

        start_cor_sen = time.time()
        print(name, "->", correct_sentence(tok, m, text, MODELS[name]["is_chat"], MODELS[name]["generate_kwargs"]),"\n")
        end_cor_sen = time.time()
        print(f"Total runtime of correct_sentence() is {end_cor_sen - start_cor_sen:.1f} s")

if __name__ == "__main__":
    main()

import json
from pathlib import Path
EXAMPLE_PATH = Path(__file__).resolve().parent.parent / "notes/fewshot_examples.json"

def build_few_template():
    """ assemble few-shot template from fewshot_examples.json"""
    data = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    examples = data["examples"]
    blocks = []
    for ex in examples:
        blocks.append(f"Original: {ex['source']}\nCorrected: {ex['gold']}")
    blocks.append("Original: {sentence}\nCorrected:")
    return "\n\n".join(blocks)

PROMPTS = {
    "zero-shot":{
        "template":"Correct only grammatical errors in this sentence and then only output the corrected sentence.\n\n{sentence}",
        "stop": None,
    },
    "few-shot":{
        "template": build_few_template(),
        "stop":"\n"
    }
}

if __name__ == "__main__":
    print(PROMPTS["few-shot"]["template"])
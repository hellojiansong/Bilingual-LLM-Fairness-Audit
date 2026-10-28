import argparse
import os
import json
import time
import pandas as pd
from google import genai

from config import EXPERIMENT_INPUTS_FILE, OUTPUT_DIR, RAW_OUTPUTS_FILE, GEMINI_MODEL
from prompts import build_prompt


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Gemini on generated pairwise resume experiments.")
    parser.add_argument("--jd-id", type=int,
                        help="Run only experiments for one JD id, e.g. 1.")
    parser.add_argument("--limit", type=int,
                        help="Run only the first N remaining experiments.")
    parser.add_argument("--sleep", type=float, default=1.0,
                        help="Seconds to wait between API calls.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Run experiments even if their experiment_id already exists in raw_outputs.jsonl.",
    )
    return parser.parse_args()


def load_completed_experiment_ids():
    """ 
    Load the experiment ids that have already been completed from the raw_outputs.jsonl file.
    """
    if not RAW_OUTPUTS_FILE.exists():
        return set()

    completed_ids = set()
    with open(RAW_OUTPUTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            experiment_id = record.get("experiment_id")
            if experiment_id and "error" not in record:
                completed_ids.add(experiment_id)

    return completed_ids


def load_env_file(path):
    """
    Load environment variables"""
    if not path.exists():
        return

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(
                key.strip(), value.strip().strip('"').strip("'"))


def main():
    args = parse_args()
    load_env_file(OUTPUT_DIR.parent / ".env")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY. Please set it in .env")

    if not EXPERIMENT_INPUTS_FILE.exists():
        raise FileNotFoundError(
            f"Missing {EXPERIMENT_INPUTS_FILE}. Run src/generate_all_inputs.py first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = genai.Client(api_key=api_key)

    df = pd.read_csv(EXPERIMENT_INPUTS_FILE)
    if args.jd_id is not None:
        df = df[df["jd_id"] == args.jd_id]

    if not args.overwrite:
        completed_ids = load_completed_experiment_ids()
        df = df[~df["experiment_id"].isin(completed_ids)]

    if args.limit is not None:
        df = df.head(args.limit)

    print(f"Running {len(df)} experiments with model {GEMINI_MODEL}")

    with open(RAW_OUTPUTS_FILE, "a", encoding="utf-8") as f:
        for _, row in df.iterrows():
            prompt = build_prompt(row)

            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                )

                record = {
                    "experiment_id": row["experiment_id"],
                    "jd_id": row["jd_id"],
                    "pair_type": row["pair_type"],
                    "bias_type": row["bias_type"],
                    "prompt_language": row["prompt_language"],
                    "prompt_condition": row["prompt_condition"],
                    "expected_answer": row["expected_answer"],
                    "raw_response": response.text,
                }

                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()

                print(f"Finished {row['experiment_id']}")
                time.sleep(args.sleep)

            except Exception as e:
                error_record = {
                    "experiment_id": row["experiment_id"],
                    "jd_id": row["jd_id"],
                    "pair_type": row["pair_type"],
                    "bias_type": row["bias_type"],
                    "prompt_language": row["prompt_language"],
                    "prompt_condition": row["prompt_condition"],
                    "error": str(e),
                }
                f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
                f.flush()

                print(f"Error in {row['experiment_id']}: {e}")


if __name__ == "__main__":
    main()

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RESUME_DIR = DATA_DIR / "resumes"
OUTPUT_DIR = BASE_DIR / "outputs"

NAMES_FILE = DATA_DIR / "names.csv"
JD_METADATA_FILE = DATA_DIR / "jd_metadata.csv"
JOB_DESCRIPTIONS_FILE = DATA_DIR / "job_descriptions.txt"

EXPERIMENT_INPUTS_FILE = OUTPUT_DIR / "experiment_inputs.csv"
RAW_OUTPUTS_FILE = OUTPUT_DIR / "raw_outputs.jsonl"
OPENAI_RAW_OUTPUTS_FILE = OUTPUT_DIR / "raw_outputs_openai.jsonl"

PROMPT_CONDITIONS = ["baseline", "eu_ai_act", "few_shot"]
PROMPT_LANGUAGES = ["English", "Dutch"]

#GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_MODEL = "gemini-2.5-flash-lite"
OPENAI_MODEL = "gpt-5.4-mini"

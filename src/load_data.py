import pandas as pd
from config import RESUME_DIR, NAMES_FILE, JD_METADATA_FILE, JOB_DESCRIPTIONS_FILE


def load_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_resumes():
    resumes = {}
    for path in RESUME_DIR.glob("*.txt"):
        resumes[path.name] = load_text_file(path)
    return resumes


def load_names():
    return pd.read_csv(NAMES_FILE)


def load_jd_metadata():
    return pd.read_csv(JD_METADATA_FILE)


def load_job_descriptions():
    if not JOB_DESCRIPTIONS_FILE.exists():
        return {}

    text = load_text_file(JOB_DESCRIPTIONS_FILE)
    descriptions = {}

    for block in text.split("=" * 60):
        block = block.strip()
        if not block or "ID:" not in block:
            continue

        jd_id = None
        lines = block.splitlines()  # split by line
        url_line_index = None
        for index, line in enumerate(lines):
            if line.startswith("ID:"):
                jd_id = int(line.split(":", 1)[1].strip())  # get jd_id
            elif line.startswith("URL"):
                url_line_index = index  # get index of URL line

        if jd_id is None:
            continue

        if "[ANONYMIZED JD]" in block:  # anonymized jd
            jd_text = block.split("[ANONYMIZED JD]", 1)[1]
        elif url_line_index is not None:  # jd with URL
            jd_text = "\n".join(lines[url_line_index + 1:])
        else:
            jd_text = "\n".join(lines)

        if "[k-ADDITIONS / GROUND TRUTH DESIGN]" in jd_text:
            jd_text = jd_text.split(
                "[k-ADDITIONS / GROUND TRUTH DESIGN]", 1)[0]

        descriptions[jd_id] = jd_text.strip()

    return descriptions

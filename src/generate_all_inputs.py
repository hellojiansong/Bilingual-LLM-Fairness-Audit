import pandas as pd

from config import OUTPUT_DIR, EXPERIMENT_INPUTS_FILE, PROMPT_CONDITIONS, PROMPT_LANGUAGES
from load_data import load_resumes, load_names, load_jd_metadata, load_job_descriptions
from generate_equal_pairs import make_equal_pair_rows
from generate_unequal_pairs import make_unequal_pair_rows


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    resumes = load_resumes()
    names_df = load_names()
    jd_df = load_jd_metadata()
    jd_descriptions = load_job_descriptions()

    all_rows = []

    for _, jd_row in jd_df.iterrows():
        jd_row = jd_row.copy()
        jd_row["jd_text"] = jd_descriptions.get(
            jd_row["jd_id"], "")  # add job description text to jd_row

        base_file = jd_row["base_resume_file"]
        superior_file = jd_row["superior_resume_file"]

        if base_file not in resumes:
            print(f"Missing base resume: {base_file}")
            continue

        if superior_file not in resumes:
            print(f"Missing superior resume: {superior_file}")
            continue

        base_resume_text = resumes[base_file]
        superior_resume_text = resumes[superior_file]

        for prompt_language in PROMPT_LANGUAGES:  # generate inputs for each prompt language
            for prompt_condition in PROMPT_CONDITIONS:  # generate inputs for each prompt condition
                equal_rows = make_equal_pair_rows(
                    jd_row=jd_row,
                    resume_text=base_resume_text,
                    names_df=names_df,
                    prompt_condition=prompt_condition,
                    prompt_language=prompt_language,
                )

                unequal_rows = make_unequal_pair_rows(
                    jd_row=jd_row,
                    base_resume_text=base_resume_text,
                    superior_resume_text=superior_resume_text,
                    names_df=names_df,
                    prompt_condition=prompt_condition,
                    prompt_language=prompt_language,
                )

                all_rows.extend(equal_rows)
                all_rows.extend(unequal_rows)

    output_df = pd.DataFrame(all_rows)
    output_df.to_csv(EXPERIMENT_INPUTS_FILE, index=False)

    print(
        f"Saved {len(output_df)} experiment inputs to {EXPERIMENT_INPUTS_FILE}")


if __name__ == "__main__":
    main()

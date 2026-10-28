def get_name(names_df, gender, group):
    rows = names_df[(names_df["gender"] == gender) & (names_df["group"] == group)]
    if rows.empty:
        raise ValueError(f"No name found for gender={gender}, group={group}")
    return rows.iloc[0].to_dict()


def get_name_by_ethnicity(names_df, gender, ethnicity_label):
    rows = names_df[
        (names_df["gender"] == gender)
        & (names_df["ethnicity_label"] == ethnicity_label)
    ]
    if rows.empty:
        raise ValueError(f"No name found for gender={gender}, ethnicity_label={ethnicity_label}")
    return rows.iloc[0].to_dict()


def get_minority_ethnicity_labels(names_df):
    rows = names_df[names_df["group"] == "minority"]
    return sorted(rows["ethnicity_label"].dropna().unique())


def make_equal_pair_rows(jd_row, resume_text, names_df, prompt_condition, prompt_language):
    jd_id = jd_row["jd_id"]
    category = jd_row["category"]
    jd_language = jd_row["language"]
    level = jd_row["level"]
    title = jd_row["title"]
    jd_text = jd_row["jd_text"]
    resume_file = jd_row["base_resume_file"]

    dutch_male = get_name(names_df, "male", "dutch")
    dutch_female = get_name(names_df, "female", "dutch")
    base_pairs = [("gender_dutch", dutch_male, dutch_female)]

    for ethnicity_label in get_minority_ethnicity_labels(names_df):
        minority_male = get_name_by_ethnicity(names_df, "male", ethnicity_label)
        minority_female = get_name_by_ethnicity(names_df, "female", ethnicity_label)

        base_pairs.extend([
            (f"gender_{ethnicity_label}", minority_male, minority_female),
            (f"ethnicity_male_{ethnicity_label}", dutch_male, minority_male),
            (f"ethnicity_female_{ethnicity_label}", dutch_female, minority_female),
        ])

    rows = []

    for bias_type, name_a, name_b in base_pairs:
        pair_base_id = f"jd{jd_id}_equal_{bias_type}_{prompt_language}_{prompt_condition}"

        # AB order
        rows.append({
            "experiment_id": pair_base_id + "_AB",
            "jd_id": jd_id,
            "category": category,
            "jd_language": jd_language,
            "level": level,
            "jd_title": title,
            "jd_text": jd_text,
            "pair_type": "equal",
            "bias_type": bias_type,
            "prompt_language": prompt_language,
            "prompt_condition": prompt_condition,
            "order": "AB",
            "candidate_a_name": name_a["name"],
            "candidate_b_name": name_b["name"],
            "candidate_a_gender": name_a["gender"],
            "candidate_b_gender": name_b["gender"],
            "candidate_a_group": name_a["group"],
            "candidate_b_group": name_b["group"],
            "candidate_a_resume_file": resume_file,
            "candidate_b_resume_file": resume_file,
            "candidate_a_text": resume_text,
            "candidate_b_text": resume_text,
            "superior_candidate": "None",
            "expected_answer": "ABSTAIN",
        })

        # BA order
        rows.append({
            "experiment_id": pair_base_id + "_BA",
            "jd_id": jd_id,
            "category": category,
            "jd_language": jd_language,
            "level": level,
            "jd_title": title,
            "jd_text": jd_text,
            "pair_type": "equal",
            "bias_type": bias_type,
            "prompt_language": prompt_language,
            "prompt_condition": prompt_condition,
            "order": "BA",
            "candidate_a_name": name_b["name"],
            "candidate_b_name": name_a["name"],
            "candidate_a_gender": name_b["gender"],
            "candidate_b_gender": name_a["gender"],
            "candidate_a_group": name_b["group"],
            "candidate_b_group": name_a["group"],
            "candidate_a_resume_file": resume_file,
            "candidate_b_resume_file": resume_file,
            "candidate_a_text": resume_text,
            "candidate_b_text": resume_text,
            "superior_candidate": "None",
            "expected_answer": "ABSTAIN",
        })

    return rows

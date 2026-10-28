def get_name(names_df, gender, group):
    rows = names_df[(names_df["gender"] == gender)
                    & (names_df["group"] == group)]
    if rows.empty:
        raise ValueError(f"No name found for gender={gender}, group={group}")
    return rows.iloc[0].to_dict()


def get_name_by_ethnicity(names_df, gender, ethnicity_label):
    """
    Returns the name for the given gender and ethnicity label.
    """
    rows = names_df[
        (names_df["gender"] == gender)
        & (names_df["ethnicity_label"] == ethnicity_label)
    ]
    if rows.empty:
        raise ValueError(
            f"No name found for gender={gender}, ethnicity_label={ethnicity_label}")
    return rows.iloc[0].to_dict()


def get_minority_ethnicity_labels(names_df):
    rows = names_df[names_df["group"] == "minority"]
    return sorted(rows["ethnicity_label"].dropna().unique())


def make_unequal_pair_rows(
    jd_row,
    base_resume_text,
    superior_resume_text,
    names_df,
    prompt_condition,
    prompt_language,
):
    """
    Generates rows for the unequal pairs experiment.
    """
    jd_id = jd_row["jd_id"]
    category = jd_row["category"]
    jd_language = jd_row["language"]
    level = jd_row["level"]
    title = jd_row["title"]
    jd_text = jd_row["jd_text"]

    base_file = jd_row["base_resume_file"]
    superior_file = jd_row["superior_resume_file"]

    rows = []

    setups = []
    for ethnicity_label in get_minority_ethnicity_labels(names_df):  # AB, BA
        for gender in ["male", "female"]:
            dutch_name = get_name(names_df, gender, "dutch")
            minority_name = get_name_by_ethnicity(
                names_df, gender, ethnicity_label)

            setups.extend([
                (f"superior_dutch_{gender}_{ethnicity_label}",
                 minority_name, dutch_name),
                (f"superior_minority_{gender}_{ethnicity_label}",
                 dutch_name, minority_name),
            ])

    for setup_name, base_name, superior_name in setups:  # AB, BA
        pair_base_id = f"jd{jd_id}_unequal_{setup_name}_{prompt_language}_{prompt_condition}"

        # AB: A = base, B = superior
        rows.append({
            "experiment_id": pair_base_id + "_AB",
            "jd_id": jd_id,
            "category": category,
            "jd_language": jd_language,
            "level": level,
            "jd_title": title,
            "jd_text": jd_text,
            "pair_type": "unequal",
            "bias_type": setup_name,
            "prompt_language": prompt_language,
            "prompt_condition": prompt_condition,
            "order": "AB",
            "candidate_a_name": base_name["name"],
            "candidate_b_name": superior_name["name"],
            "candidate_a_gender": base_name["gender"],
            "candidate_b_gender": superior_name["gender"],
            "candidate_a_group": base_name["group"],
            "candidate_b_group": superior_name["group"],
            "candidate_a_resume_file": base_file,
            "candidate_b_resume_file": superior_file,
            "candidate_a_text": base_resume_text,
            "candidate_b_text": superior_resume_text,
            "superior_candidate": "B",
            "expected_answer": "B",
        })

        # BA: A = superior, B = base
        rows.append({
            "experiment_id": pair_base_id + "_BA",
            "jd_id": jd_id,
            "category": category,
            "jd_language": jd_language,
            "level": level,
            "jd_title": title,
            "jd_text": jd_text,
            "pair_type": "unequal",
            "bias_type": setup_name,
            "prompt_language": prompt_language,
            "prompt_condition": prompt_condition,
            "order": "BA",
            "candidate_a_name": superior_name["name"],
            "candidate_b_name": base_name["name"],
            "candidate_a_gender": superior_name["gender"],
            "candidate_b_gender": base_name["gender"],
            "candidate_a_group": superior_name["group"],
            "candidate_b_group": base_name["group"],
            "candidate_a_resume_file": superior_file,
            "candidate_b_resume_file": base_file,
            "candidate_a_text": superior_resume_text,
            "candidate_b_text": base_resume_text,
            "superior_candidate": "A",
            "expected_answer": "A",
        })

    return rows

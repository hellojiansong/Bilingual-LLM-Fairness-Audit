# LLM Resume Screening Bias Audit

![Python](https://img.shields.io/badge/Language-Python-3776AB?style=flat&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/LLM-OpenAI-412991?style=flat&logo=openai&logoColor=white)
![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4?style=flat&logo=googlegemini&logoColor=white)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Jupyter](https://img.shields.io/badge/Analysis-Jupyter-F37626?style=flat&logo=jupyter&logoColor=white)

**Academic project | MSc Computer Science (Data Science) | Leiden University**

This repository contains the code, experimental inputs, model outputs, and evaluation results for a controlled pairwise audit of LLM-based resume screening in Dutch and English recruitment contexts.

The experiment evaluates demographic selection differences, presentation-order sensitivity, and decision validity in Gemini and OpenAI models. The full study includes:

- **20 job descriptions** across IT, Healthcare, and Administration
- **40 synthetic resumes**, one base and one superior resume for each job description
- **5,280 test instances per model** and **10,560 model evaluations** across both models
- **Two prompt languages:** Dutch and English
- **Three prompt conditions:** Baseline, EU AI Act-inspired, and Few-shot
- **Two candidate presentation orders:** AB and BA

## Key Findings

| Model | Validity | Abstention Rate | Selection Rate Difference (ΔSR) | Inconsistency Rate |
| --- | ---: | ---: | ---: | ---: |
| Gemini | 43.4% | 99.8% | -0.00084 | 16.4% |
| OpenAI | 56.4% | 99.7% | -0.00083 | 20.8% |

Both models almost always abstained when candidate qualifications were identical, but were less reliable at identifying the superior resume when qualifications differed. Fairness-oriented prompts did not improve decision validity in this experiment. Under few-shot prompting, validity fell from **67.5% to 8.0%** for Gemini and from **70.6% to 38.1%** for OpenAI.

Near-zero aggregate selection differences on equal-qualification pairs **do not establish the absence of bias**. Subgroup analysis of unequal-qualification pairs suggested that identifying the superior candidate could be more reliable when the stronger resume carried a Dutch-signaled name.

## Experimental Design

For each job description, the pipeline creates **22 candidate-pair configurations**: 10 equal-qualification configurations and 12 unequal-qualification configurations. Each is evaluated in two orders, two prompt languages, and three prompt conditions:

```text
20 job descriptions × 22 pair configurations × 2 orders × 2 languages × 3 prompts
= 5,280 test instances per model
= 10,560 evaluations across two models
```

- **Equal-qualification pairs:** Identical resume content, different demographic name signals. The expected decision is `ABSTAIN`.
- **Unequal-qualification pairs:** One base resume and one superior resume with additional job-relevant qualifications. The expected decision is the superior candidate (`A` or `B`).
- **Demographic name signals:** Dutch, Turkish, Moroccan, and Indonesian, with male and female names.
- **Models:** `gemini-2.5-flash-lite` and `gpt-5.4-mini`, accessed through hosted APIs; no fine-tuning was performed.

The evaluation measures **Validity** on unequal pairs, **Abstention Rate** and **Selection Rate Difference (ΔSR)** on equal pairs, and **Inconsistency Rate** across AB/BA comparisons.

## 1. Environment Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

In VS Code, select the project interpreter using `Cmd + Shift + P` → **Python: Select Interpreter** → `.venv`.

## 2. API Keys

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**Never commit `.env` or real API credentials.**

## 3. Input Data

Check that all resume files listed in `data/jd_metadata.csv` exist. The full experiment requires:

```text
data/jd_metadata.csv
data/job_descriptions.txt
data/names.csv
data/resumes/1.1.txt ... 20.2.txt
```

For each job description, `x.1.txt` is the base resume and `x.2.txt` is the superior resume with additional job-relevant qualifications. The data loader extracts anonymized job-description text and excludes ground-truth construction notes so they are not revealed to the model.

The resumes are synthetic. Job descriptions were sourced from real postings and anonymized; review source permissions before redistributing the underlying text.

## 4. Generate Experiment Inputs

```bash
python src/generate_all_inputs.py
```

This writes `outputs/experiment_inputs.csv`. Each job description generates **264 test instances**:

```text
22 configurations × 2 presentation orders × 2 languages × 3 prompts = 264
20 job descriptions × 264 = 5,280 instances per model
```

After order expansion, the 22 configurations become 20 equal-qualification and 24 unequal-qualification ordered pairs per job description.

## 5. Run Gemini Experiments

Smoke test:

```bash
python src/run_gemini.py --jd-id 1 --limit 1 --sleep 0
```

Run all Gemini experiments, a single job description, or a limited batch:

```bash
python src/run_gemini.py
python src/run_gemini.py --jd-id 1
python src/run_gemini.py --limit 5
python src/run_gemini.py --sleep 2
```

The runner writes `outputs/raw_outputs.jsonl` and skips previously successful experiment IDs by default. Use `python src/run_gemini.py --overwrite` to rerun them.

## 6. Run OpenAI Experiments

Smoke test:

```bash
python src/run_openai.py --jd-id 1 --limit 1 --sleep 0
```

Other options:

```bash
python src/run_openai.py
python src/run_openai.py --jd-id 1
python src/run_openai.py --limit 5
python src/run_openai.py --overwrite
```

The runner writes `outputs/raw_outputs_openai.jsonl` and skips previously successful experiment IDs by default.

**Note:** The `raw_outputs*.jsonl` files above are generated during execution; the repository currently includes their **cleaned** counterparts, not the uncleaned raw files.

## 7. Clean Raw Outputs

After collecting raw model outputs, run:

```bash
python src/clean_raw_data.py
```

The script removes error records and deduplicates successful records by `experiment_id`, keeping the most recent successful record. It produces:

```text
outputs/cleaned_raw_outputs.jsonl
outputs/cleaned_raw_outputs_openai.jsonl
```

These cleaned files are included in the repository so that results can be inspected without repeating paid API calls.

## 8. Evaluation and Results

The evaluation code is now located in **`analysis/`**:

```text
analysis/metrics_results_analysis.ipynb
analysis/metrics_results_analysis.py
```

The analysis combines:

```text
outputs/experiment_inputs.csv
outputs/cleaned_raw_outputs.jsonl
outputs/cleaned_raw_outputs_openai.jsonl
```

It computes validity, abstention rate, selection rate difference, and AB/BA inconsistency. The six final summary tables are in **`results/`**:

```text
results/summary_by_model.csv
results/summary_by_prompt.csv
results/summary_by_language.csv
results/summary_by_category.csv
results/summary_equal_bias_type.csv
results/summary_unequal_bias_type.csv
```

The analysis notebook and script were originally run in a Colab-style environment; local users may need to update input/output paths before rerunning the analysis. In particular, the source files may still refer to the former `result/` directory.

## 9. Project Structure

```text
Bilingual-LLM-Fairness-Audit/
├── README.md
├── requirements.txt
├── .gitignore                      
├── analysis/
│   ├── metrics_results_analysis.ipynb
│   └── metrics_results_analysis.py
├── data/
│   ├── jd_metadata.csv
│   ├── job_descriptions.txt
│   ├── names.csv
│   └── resumes/
│       ├── 1.1.txt
│       ├── 1.2.txt
│       ├── ...
│       ├── 20.1.txt
│       └── 20.2.txt
├── outputs/
│   ├── experiment_inputs.csv
│   ├── cleaned_raw_outputs.jsonl
│   └── cleaned_raw_outputs_openai.jsonl
├── results/
│   ├── summary_by_model.csv
│   ├── summary_by_prompt.csv
│   ├── summary_by_language.csv
│   ├── summary_by_category.csv
│   ├── summary_equal_bias_type.csv
│   └── summary_unequal_bias_type.csv
└── src/
    ├── config.py
    ├── load_data.py
    ├── generate_equal_pairs.py
    ├── generate_unequal_pairs.py
    ├── generate_all_inputs.py
    ├── prompts.py
    ├── run_gemini.py
    ├── run_openai.py
    └── clean_raw_data.py
```

## 10. Source File Overview

| File | Purpose |
| --- | --- |
| `src/config.py` | Defines project paths, output files, prompt conditions, prompt languages, and model names. |
| `src/load_data.py` | Loads job descriptions, resume files, names, and JD metadata. |
| `src/generate_equal_pairs.py` | Builds equal-qualification pairs with different name signals; expected decision: `ABSTAIN`. |
| `src/generate_unequal_pairs.py` | Builds base-versus-superior resume pairs; expected decision: the superior candidate. |
| `src/generate_all_inputs.py` | Combines candidate pairs, languages, and prompt conditions into experiment inputs. |
| `src/prompts.py` | Builds English and Dutch Baseline, EU AI Act-inspired, and Few-shot prompts. |
| `src/run_gemini.py` | Calls Gemini and records model responses. |
| `src/run_openai.py` | Calls OpenAI and records model responses. |
| `src/clean_raw_data.py` | Cleans and deduplicates model output records. |
| `analysis/metrics_results_analysis.py` | Computes and summarizes the evaluation metrics. |
| `analysis/metrics_results_analysis.ipynb` | Notebook version of the evaluation workflow. |

## Academic Context and Contributions

This is a collaborative academic project from the MSc Computer Science (Data Science) programme at Leiden University.

- **Xiatong Xiong:** Data collection and dataset generation.
- **Qi Liu:** Data processing and experiment execution pipeline.
- **Jian Song:** Prompting strategies and API integration.
- **Nurifeiya Anwaier:** Evaluation metrics and results analysis.
- **All authors:** Research report writing.

The findings are from a controlled research simulation, **not** a validated system for real-world hiring decisions. High abstention on identical resumes does not guarantee demographic fairness in other settings.

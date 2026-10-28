import json
from pathlib import Path


def clean_jsonl(file_path):
    input_path = Path(file_path)
    if not input_path.exists():
        print(f"file not found: {input_path}")
        return

    output_path = input_path.parent / f"cleaned_{input_path.name}"

    # Used to store records of successful operations; a dictionary is used to ensure unique IDs (retaining only the most recent successful record)
    successful_records = {}
    error_count = 0
    total_raw_lines = 0

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            total_raw_lines += 1
            try:
                record = json.loads(line.strip())
                # Check for the “Error”
                if "error" in record:
                    error_count += 1
                    continue

                # If there are no errors, add it to the dictionary (if the ID is duplicated, the later successful entry will overwrite the earlier one).
                exp_id = record.get("experiment_id")
                if exp_id:
                    successful_records[exp_id] = record
            except json.JSONDecodeError:
                error_count += 1
                continue

    with open(output_path, "w", encoding="utf-8") as f:
        for record in successful_records.values():
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f" {input_path.name}")
    print(
        f"Total number of original records (including errors/duplicates): {total_raw_lines}")
    print(f"Number of rows removed: {error_count}")
    print(f"Final Valid Unique Data Volume: {len(successful_records)}")
    print(f"saved: {output_path}\n")


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent

    files_to_clean = [
        base_path / "outputs" / "raw_outputs.jsonl",
        base_path / "outputs" / "raw_outputs_openai.jsonl"
    ]

    for file in files_to_clean:
        clean_jsonl(file)

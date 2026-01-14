import csv
import json
import re
from pathlib import Path


def summarize_folder(input_dir: str, output_csv: str) -> None:
    input_path = Path(input_dir)
    pattern = re.compile(r"alignment_result_(Itinerary_\d{2})\.json$")

    rows = []
    for file_path in input_path.glob("alignment_result_Itinerary_*.json"):
        m = pattern.search(file_path.name)
        if not m:
            continue

        itinerary_id = m.group(1)

        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"{file_path.name} is not a list in JSON.")

        extracted_num = data[0]["extracted_requirement_num"]
        valid_num = len(data[0]["valid_requirements"] or [])
        missing_num = len(data[0]["missing_requirements"] or [])
        satisfied_num = data[1]["satisfied_requirements_num"]

        alignment_rate = satisfied_num / (extracted_num + missing_num)

        rows.append(
            {
                "itinerary_id": itinerary_id,
                "extracted_num": extracted_num,
                "valid_num": valid_num,
                "missing_num": missing_num,
                "satisfied_num": satisfied_num,
                "alignment_rate": alignment_rate,
            }
        )

    # Sort by itinerary number (01..48)
    def sort_key(r):
        return int(r["itinerary_id"].split("_")[-1])

    rows.sort(key=sort_key)

    fieldnames = [
        "itinerary_id",
        "extracted_num",
        "valid_num",
        "missing_num",
        "satisfied_num",
        "alignment_rate",
    ]

    out_path = Path(output_csv)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    summarize_folder(
        input_dir="alignment_results",
        output_csv="new_alignment_summary.csv",
    )

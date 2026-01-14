import csv
import json
import re
from pathlib import Path


def summarize_folder(input_dir: str, output_csv: str) -> None:
    input_path = Path(input_dir)
    pattern = re.compile(r"verification_result_(Itinerary_\d{2})\.json$")

    rows = []
    for file_path in input_path.glob("verification_result_Itinerary_*.json"):
        m = pattern.search(file_path.name)
        if not m:
            continue

        itinerary_id = m.group(1)

        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"{file_path.name} is not a list in JSON.")

        total = len(data)
        addr_provided_count = 0
        addr_fail_count = 0

        for item in data:
            addr_provided = item["address_provided"]
            if addr_provided is True:
                addr_provided_count += 1
            val = item["address_match_place"]
            if val is False and addr_provided is True:
                addr_fail_count += 1

        fail_rate = (
            (addr_fail_count / addr_provided_count)
            if addr_provided_count > 0
            else "null"
        )

        rows.append(
            {
                "itinerary_id": itinerary_id,
                "total": total,
                "addr_provided_count": addr_provided_count,
                "addr_fail_count": addr_fail_count,
                "fail_rate": fail_rate,
            }
        )

    # Sort by itinerary number (01..48)
    def sort_key(r):
        return int(r["itinerary_id"].split("_")[-1])

    rows.sort(key=sort_key)

    fieldnames = [
        "itinerary_id",
        "total",
        "addr_provided_count",
        "addr_fail_count",
        "fail_rate",
    ]

    out_path = Path(output_csv)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    summarize_folder(
        input_dir="verification_results",
        output_csv="new_verification_summary.csv",
    )

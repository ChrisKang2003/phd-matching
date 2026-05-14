# utils/export_professors_csv.py

import json
import pandas as pd
from pathlib import Path


INPUT_PATH = Path("data/entities/professors.json")
OUTPUT_PATH = Path("data/processed/professors.csv")


def normalize_professor_record(record):
    """
    Converts one professor JSON record into one CSV row.
    Adjust field names here if your professors.json uses different keys.
    """
    return {
        "professor_name": record.get("name", ""),
        "title": record.get("title", ""),
        "email": record.get("email", ""),
        "university": record.get("university", ""),
        "department": record.get("department", ""),
        "profile_url": record.get("url", ""),
        "research_interests": " ".join(record.get("research_interests", []))
        if isinstance(record.get("research_interests", []), list)
        else record.get("research_interests", ""),
        "publications": " ".join(record.get("publications", []))
        if isinstance(record.get("publications", []), list)
        else record.get("publications", ""),
        "professor_profile": " ".join(
            str(x)
            for x in [
                record.get("name", ""),
                record.get("title", ""),
                record.get("department", ""),
                record.get("research_summary", ""),
                record.get("research_interests", ""),
                record.get("bio", ""),
            ]
            if x
        ),
    }


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_PATH}. Run the pipeline first with: python main.py"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handles either a list of professors or a dictionary containing professors
    if isinstance(data, dict):
        if "professors" in data:
            professors = data["professors"]
        else:
            professors = list(data.values())
    elif isinstance(data, list):
        professors = data
    else:
        raise ValueError("Unsupported professors.json format.")

    rows = [normalize_professor_record(record) for record in professors]
    df = pd.DataFrame(rows)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Exported {len(df)} professors to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
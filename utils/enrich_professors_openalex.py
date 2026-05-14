import time
import requests
import pandas as pd
from pathlib import Path
from urllib.parse import quote


INPUT_CSV = Path("data/processed/professors.csv")
OUTPUT_CSV = Path("data/processed/professors_enriched.csv")


def search_openalex_author(name, university=""):
    query = quote(f"{name} {university}")
    url = f"https://api.openalex.org/authors?search={query}&per-page=1"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    if not results:
        return None

    return results[0]


def get_author_works(author_id, max_works=5):
    url = (
        "https://api.openalex.org/works"
        f"?filter=authorships.author.id:{author_id}"
        f"&sort=publication_year:desc"
        f"&per-page={max_works}"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def summarize_work(work):
    title = work.get("title", "")

    concepts = [
        concept.get("display_name", "")
        for concept in work.get("concepts", [])[:5]
        if concept.get("display_name")
    ]

    return f"{title}. Topics: {', '.join(concepts)}"


def enrich_professor(row):
    name = row.get("professor_name", "")
    university = row.get("university", "")

    print(f"Enriching: {name}")

    author = search_openalex_author(name, university)

    if not author:
        return row.get("professor_profile", "")

    author_id = author.get("id", "")
    works = get_author_works(author_id, max_works=5)

    work_summaries = [summarize_work(work) for work in works]

    enriched_profile = f"""
    Professor: {name}
    University: {university}
    Discipline: {row.get("discipline", "")}
    Existing profile: {row.get("professor_profile", "")}
    Recent publications and topics: {" ".join(work_summaries)}
    """

    return " ".join(enriched_profile.split())


def main():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)

    if "professor_name" not in df.columns:
        raise ValueError("CSV must contain professor_name column")

    enriched_profiles = []

    for _, row in df.iterrows():
        try:
            enriched_profiles.append(enrich_professor(row))
            time.sleep(0.2)
        except Exception as e:
            print(f"Failed to enrich {row.get('professor_name', '')}: {e}")
            enriched_profiles.append(row.get("professor_profile", ""))

    df["professor_profile"] = enriched_profiles

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"Saved enriched professor data to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
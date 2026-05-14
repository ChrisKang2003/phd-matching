import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path


FACULTY_URLS = [
    {
        "university": "Stevens Institute of Technology",
        "discipline": "CS & AI",
        "url": "https://www.stevens.edu/school-engineering-science/departments/computer-science/faculty",
    },
    {
        "university": "Stanford University",
        "discipline": "CS & AI",
        "url": "https://cs.stanford.edu/directory/faculty",
    },

    {
        "university": "Carnegie Mellon University",
        "discipline": "CS & AI",
        "url": "https://www.cs.cmu.edu/directory/faculty",
    },

    {
        "university": "Princeton University",
        "discipline": "Electrical Engineering",
        "url": "https://ece.princeton.edu/people/faculty",
    },
    {
        "university": "Massachusetts Institute of Technology",
        "discipline": "CS & AI",
        "url": "https://www.eecs.mit.edu/role/faculty/"
    },
    {
        "university": "Cornell University",
        "discipline": "CS & AI",
        "url": "https://www.cs.cornell.edu/directory"
    },
    {
        "university": "University of Washington",
        "discipline": "CS & AI",
        "url": "https://www.cs.washington.edu/people/faculty-members/"
    },
    {
        "university": "University of California Berkeley",
        "discipline": "CS & AI",
        "url": "https://www2.eecs.berkeley.edu/Faculty/Lists/faculty.html"
    },
    {
        "university": "Johns Hopkins University",
        "discipline": "Bio & Health",
        "url": "https://www.bme.jhu.edu/people/faculty/"
    },
    {
        "university": "Duke University",
        "discipline": "Bio & Health",
        "url": "https://bme.duke.edu/people/"
    },
    {
        "university": "University of Pennsylvania",
        "discipline": "Business & Finance",
        "url": "https://www.wharton.upenn.edu/faculty-directory/"
    },
    {
        "university": "Massachusetts Institute of Technology Sloan",
        "discipline": "Business & Finance",
        "url": "https://mitsloan.mit.edu/faculty/faculty-directory"
    }
]


OUTPUT_PATH = Path("data/processed/professors.csv")


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else ""


def looks_like_professor_block(text):
    title_words = [
        "professor",
        "assistant professor",
        "associate professor",
        "lecturer",
        "faculty",
        "research",
        "director",
    ]
    return any(word in text.lower() for word in title_words)


def crawl_faculty_page(url, university, discipline):
    print(f"Crawling: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    professors = []

    cards = soup.find_all(["article", "div", "li"])

    for card in cards:
        text = clean_text(card.get_text(" ", strip=True))

        if len(text) < 40:
            continue

        if not looks_like_professor_block(text):
            continue

        links = card.find_all("a", href=True)
        profile_url = urljoin(url, links[0]["href"]) if links else url

        possible_name = ""
        heading = card.find(["h2", "h3", "h4", "a"])
        if heading:
            possible_name = clean_text(heading.get_text(" ", strip=True))

        if not possible_name or len(possible_name.split()) < 2:
            continue

        email = extract_email(text)

        professor_profile = text[:1200]

        professors.append({
            "professor_name": possible_name,
            "discipline": discipline,
            "university": university,
            "email": email,
            "profile_url": profile_url,
            "professor_profile": professor_profile,
        })

    deduped = {}
    for professor in professors:
        key = professor["professor_name"].lower()
        if key not in deduped:
            deduped[key] = professor

    return list(deduped.values())


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_professors = []

    for source in FACULTY_URLS:
        try:
            professors = crawl_faculty_page(
                url=source["url"],
                university=source["university"],
                discipline=source["discipline"],
            )
            all_professors.extend(professors)
            print(f"Found {len(professors)} professors")
        except Exception as e:
            print(f"Failed to crawl {source['url']}: {e}")

    df = pd.DataFrame(all_professors)

    if df.empty:
        raise RuntimeError(
            "No professors found. Try another faculty URL or inspect the page HTML."
        )

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} professors to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
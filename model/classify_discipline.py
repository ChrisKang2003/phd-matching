DISCIPLINE_KEYWORDS = {
    "CS & AI": [
        "machine learning", "deep learning", "artificial intelligence",
        "nlp", "natural language processing", "computer vision",
        "security", "systems", "recommendation", "retrieval"
    ],
    "Electrical Engineering": [
        "signal", "signals", "circuit", "circuits", "wireless",
        "communications", "control", "sensor", "power", "hardware"
    ],
    "Bio & Health": [
        "biology", "biomedical", "health", "clinical", "medical",
        "genomics", "imaging", "diagnosis", "neuroscience"
    ],
    "Business & Finance": [
        "finance", "business", "market", "markets", "economics",
        "management", "risk", "analytics", "investment"
    ],
}


def classify_discipline(student_profile: str) -> str:
    text = student_profile.lower()
    best_discipline = "CS & AI"
    best_score = -1

    for discipline, keywords in DISCIPLINE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > best_score:
            best_score = score
            best_discipline = discipline

    return best_discipline


if __name__ == "__main__":
    profile = "I am interested in deep learning, NLP, and recommendation systems."
    print(classify_discipline(profile))

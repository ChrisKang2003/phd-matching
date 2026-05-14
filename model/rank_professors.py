import pandas as pd
from sentence_transformers import CrossEncoder

MODEL_PATH = "model/checkpoints/rightfit_cross_encoder"
PROFESSORS_PATH = "data/processed/professors.csv"

PROFESSOR_NAME_COL = "professor_name"
PROFESSOR_TEXT_COL = "professor_profile"
DISCIPLINE_COL = "discipline"


def rank_professors(student_profile: str, discipline=None, top_k: int = 5):
    professors = pd.read_csv(PROFESSORS_PATH)

    if discipline and DISCIPLINE_COL in professors.columns:
        professors = professors[professors[DISCIPLINE_COL].str.lower() == discipline.lower()]

    if PROFESSOR_TEXT_COL not in professors.columns:
        raise ValueError(f"professors.csv must contain column: {PROFESSOR_TEXT_COL}")

    model = CrossEncoder(MODEL_PATH)

    pairs = [
        (student_profile, str(row[PROFESSOR_TEXT_COL]))
        for _, row in professors.iterrows()
    ]

    scores = model.predict(pairs)
    professors = professors.copy()
    professors["match_score"] = scores

    return professors.sort_values("match_score", ascending=False).head(top_k)


if __name__ == "__main__":
    student = """
    I am interested in deep learning, computer vision, medical imaging,
    and AI systems for healthcare diagnostics.
    """

    results = rank_professors(student, discipline=None, top_k=5)
    print(results[[PROFESSOR_NAME_COL, "match_score"]])

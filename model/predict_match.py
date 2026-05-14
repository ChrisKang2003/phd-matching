from sentence_transformers import CrossEncoder

MODEL_PATH = "model/checkpoints/rightfit_cross_encoder"


def predict_match(student_profile: str, professor_profile: str) -> float:
    model = CrossEncoder(MODEL_PATH)
    score = model.predict([(student_profile, professor_profile)])[0]
    return float(score)


if __name__ == "__main__":
    student = """
    I am interested in natural language processing, information retrieval,
    recommender systems, and machine learning for academic search.
    """

    professor = """
    The professor works on neural ranking, information retrieval,
    language models, recommender systems, and search engines.
    """

    score = predict_match(student, professor)
    print(f"Matching score: {score:.4f}")

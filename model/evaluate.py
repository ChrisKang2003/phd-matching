import pandas as pd
from sentence_transformers import CrossEncoder
from model.config import ModelConfig


def recall_at_k(df: pd.DataFrame, k: int = 5) -> float:
    hits = 0
    total = 0

    for _, group in df.groupby("query_id"):
        ranked = group.sort_values("score", ascending=False).head(k)
        if ranked["label"].max() > 0:
            hits += 1
        total += 1

    return hits / total if total else 0.0


def evaluate_ranking(test_path: str, model_path: str, k: int = 5):
    config = ModelConfig()
    df = pd.read_csv(test_path)

    required = ["query_id", config.student_col, config.professor_col, config.label_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    model = CrossEncoder(model_path)

    pairs = list(zip(df[config.student_col].astype(str), df[config.professor_col].astype(str)))
    df["score"] = model.predict(pairs)
    df["label"] = df[config.label_col]

    score = recall_at_k(df, k=k)
    print(f"Recall@{k}: {score:.4f}")
    return score


if __name__ == "__main__":
    evaluate_ranking(
        test_path="data/processed/test_pairs.csv",
        model_path="model/checkpoints/rightfit_cross_encoder",
        k=5
    )

import pandas as pd
from sentence_transformers import InputExample
from sklearn.model_selection import train_test_split
from config import ModelConfig


def load_pairs(config: ModelConfig) -> pd.DataFrame:
    df = pd.read_csv(config.data_path)

    required = [config.student_col, config.professor_col, config.label_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    df = df.dropna(subset=required).copy()
    df[config.student_col] = df[config.student_col].astype(str)
    df[config.professor_col] = df[config.professor_col].astype(str)
    df[config.label_col] = df[config.label_col].astype(float)

    return df


def make_examples(df: pd.DataFrame, config: ModelConfig):
    return [
        InputExample(
            texts=[row[config.student_col], row[config.professor_col]],
            label=float(row[config.label_col])
        )
        for _, row in df.iterrows()
    ]


def split_dataset(df: pd.DataFrame, config: ModelConfig):
    stratify = None
    if config.label_col in df.columns and df[config.label_col].nunique() <= 10:
        stratify = df[config.label_col]

    return train_test_split(
        df,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=stratify
    )

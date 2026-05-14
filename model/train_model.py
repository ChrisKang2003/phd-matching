print("train_model.py started")

print("Importing os...")
import os

print("Importing torch DataLoader...")
from torch.utils.data import DataLoader

print("Importing CrossEncoder...")
from sentence_transformers import CrossEncoder

print("Importing evaluator...")
from sentence_transformers.cross_encoder.evaluation import CEBinaryClassificationEvaluator

print("Importing project files...")
from config import ModelConfig
from dataset import load_pairs, make_examples, split_dataset

print("All imports completed")


def main():
    print("Loading config...")
    config = ModelConfig()

    print(f"Looking for dataset at: {config.data_path}")

    if not os.path.exists(config.data_path):
        raise FileNotFoundError(
            f"Training CSV not found: {config.data_path}\n"
            "Move your CSV to data/training_pairs/student_professor_pairs.csv"
        )

    os.makedirs(config.output_dir, exist_ok=True)

    print("Loading dataset...")
    df = load_pairs(config)

    print(f"Loaded {len(df)} rows")
    print(df.head())

    train_df, test_df = split_dataset(df, config)

    print(f"Training examples: {len(train_df)}")
    print(f"Testing examples: {len(test_df)}")

    train_examples = make_examples(train_df, config)
    test_examples = make_examples(test_df, config)

    train_loader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=config.batch_size
    )

    print("Loading MiniLM cross-encoder...")
    model = CrossEncoder(
        config.base_model,
        num_labels=1,
        max_length=config.max_length
    )

    evaluator = CEBinaryClassificationEvaluator.from_input_examples(
        test_examples,
        name="rightfit-validation"
    )

    warmup_steps = int(len(train_loader) * config.epochs * 0.1)

    print("Fine-tuning model...")
    model.fit(
        train_dataloader=train_loader,
        evaluator=evaluator,
        epochs=config.epochs,
        warmup_steps=warmup_steps,
        optimizer_params={"lr": config.learning_rate},
        output_path=config.output_dir,
        save_best_model=True
    )

    print(f"Saved best model to {config.output_dir}")


if __name__ == "__main__":
    main()
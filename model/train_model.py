print("train_model.py started")

import os
import shutil
from torch.utils.data import DataLoader
from sentence_transformers import CrossEncoder
from sentence_transformers.cross_encoder.evaluation import CEBinaryClassificationEvaluator

from config import ModelConfig
from dataset import load_pairs, make_examples, split_dataset


def main():
    config = ModelConfig()

    if not os.path.exists(config.data_path):
        raise FileNotFoundError(f"Missing training CSV: {config.data_path}")

    # Clear broken old checkpoint
    if os.path.exists(config.output_dir):
        shutil.rmtree(config.output_dir)

    os.makedirs(config.output_dir, exist_ok=True)

    print("Loading dataset...")
    df = load_pairs(config)
    print(f"Loaded {len(df)} rows")

    train_df, test_df = split_dataset(df, config)
    train_examples = make_examples(train_df, config)
    test_examples = make_examples(test_df, config)

    train_loader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=config.batch_size
    )

    print("Loading base model...")
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

    print("Training...")
    model.fit(
        train_dataloader=train_loader,
        evaluator=evaluator,
        epochs=config.epochs,
        warmup_steps=warmup_steps,
        optimizer_params={"lr": config.learning_rate},
        save_best_model=True,
        output_path=config.output_dir
    )

    print("Force-saving final model...")
    model.save(config.output_dir)

    print(f"Model saved to: {config.output_dir}")

    expected_config = os.path.join(config.output_dir, "config.json")
    if not os.path.exists(expected_config):
        raise RuntimeError("Model did not save correctly: config.json missing")

    print("Model save verified.")


if __name__ == "__main__":
    main()
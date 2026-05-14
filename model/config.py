from dataclasses import dataclass

@dataclass
class ModelConfig:
    data_path: str = "data/training_pairs/student_professor_pairs.csv"
    output_dir: str = "model/checkpoints/rightfit_cross_encoder"
    base_model: str = "cross-encoder/ms-marco-MiniLM-L6-v2"

    student_col: str = "student_profile"
    professor_col: str = "professor_profile"
    label_col: str = "label"
    discipline_col: str = "discipline"

    batch_size: int = 16
    epochs: int = 3
    learning_rate: float = 2e-5
    max_length: int = 512
    test_size: float = 0.2
    random_state: int = 42

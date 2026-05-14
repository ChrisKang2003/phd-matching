---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:160
- loss:BinaryCrossEntropyLoss
base_model: cross-encoder/ms-marco-MiniLM-L6-v2
pipeline_tag: text-ranking
library_name: sentence-transformers
metrics:
- accuracy
- accuracy_threshold
- f1
- f1_threshold
- precision
- recall
- average_precision
model-index:
- name: CrossEncoder based on cross-encoder/ms-marco-MiniLM-L6-v2
  results:
  - task:
      type: cross-encoder-binary-classification
      name: Cross Encoder Binary Classification
    dataset:
      name: rightfit validation
      type: rightfit-validation
    metrics:
    - type: accuracy
      value: 0.9
      name: Accuracy
    - type: accuracy_threshold
      value: 3.001263380050659
      name: Accuracy Threshold
    - type: f1
      value: 0.9130434782608695
      name: F1
    - type: f1_threshold
      value: 0.7558400630950928
      name: F1 Threshold
    - type: precision
      value: 0.875
      name: Precision
    - type: recall
      value: 0.9545454545454546
      name: Recall
    - type: average_precision
      value: 0.963438712443075
      name: Average Precision
---

# CrossEncoder based on cross-encoder/ms-marco-MiniLM-L6-v2

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) <!-- at revision c5ee24cb16019beea0893ab7796b1df96625c6b8 -->
- **Maximum Sequence Length:** 512 tokens
- **Number of Output Labels:** 1 label
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Documentation:** [Cross Encoder Documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Cross Encoders on Hugging Face](https://huggingface.co/models?library=sentence-transformers&other=cross-encoder)

### Full Model Architecture

```
CrossEncoder(
  (0): Transformer({'transformer_task': 'sequence-classification', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'logits'}}, 'module_output_name': 'scores', 'architecture': 'BertForSequenceClassification'})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import CrossEncoder

# Download from the 🤗 Hub
model = CrossEncoder("cross_encoder_model_id")
# Get scores for pairs of inputs
pairs = [
    ['I am interested in computational biology, neuroscience, and biomedical engineering. My projects focus on AI-driven applications and research systems.', 'Research interests include wireless communications, cyber-physical systems, embedded systems, and signal processing. Current work focuses on advanced interdisciplinary research.'],
    ['I am interested in investment systems, data analytics, and business intelligence. My projects focus on AI-driven applications and research systems.', 'Research interests include computer vision, recommendation systems, information retrieval, and natural language processing. Current work focuses on advanced interdisciplinary research.'],
    ['I am interested in sensors, circuits, and control systems. My projects focus on AI-driven applications and research systems.', 'Research interests include risk modeling, business intelligence, economics, and investment systems. Current work focuses on advanced interdisciplinary research.'],
    ['I am interested in natural language processing, security, and machine learning. My projects focus on AI-driven applications and research systems.', 'Research interests include wireless communications, power systems, embedded systems, and cyber-physical systems. Current work focuses on advanced interdisciplinary research.'],
    ['I am interested in business intelligence, risk modeling, and economics. My projects focus on AI-driven applications and research systems.', 'Research interests include investment systems, economics, market prediction, and business intelligence. Current work focuses on advanced interdisciplinary research.'],
]
scores = model.predict(pairs)
print(scores)
# [-3.7655 -0.6616 -2.8264 -3.5969  6.9191]

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'I am interested in computational biology, neuroscience, and biomedical engineering. My projects focus on AI-driven applications and research systems.',
    [
        'Research interests include wireless communications, cyber-physical systems, embedded systems, and signal processing. Current work focuses on advanced interdisciplinary research.',
        'Research interests include computer vision, recommendation systems, information retrieval, and natural language processing. Current work focuses on advanced interdisciplinary research.',
        'Research interests include risk modeling, business intelligence, economics, and investment systems. Current work focuses on advanced interdisciplinary research.',
        'Research interests include wireless communications, power systems, embedded systems, and cyber-physical systems. Current work focuses on advanced interdisciplinary research.',
        'Research interests include investment systems, economics, market prediction, and business intelligence. Current work focuses on advanced interdisciplinary research.',
    ]
)
# [{'corpus_id': ..., 'score': ...}, {'corpus_id': ..., 'score': ...}, ...]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### Metrics

#### Cross Encoder Binary Classification

* Dataset: `rightfit-validation`
* Evaluated with [<code>CEBinaryClassificationEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CEBinaryClassificationEvaluator)

| Metric                | Value      |
|:----------------------|:-----------|
| accuracy              | 0.9        |
| accuracy_threshold    | 3.0013     |
| f1                    | 0.913      |
| f1_threshold          | 0.7558     |
| precision             | 0.875      |
| recall                | 0.9545     |
| **average_precision** | **0.9634** |

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 160 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 100 samples:
  |          | sentence_0                                                                         | sentence_1                                                                         | label                                                          |
  |:---------|:-----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type     | string                                                                             | string                                                                             | float                                                          |
  | modality | text                                                                               | text                                                                               |                                                                |
  | details  | <ul><li>min: 26 tokens</li><li>mean: 27.85 tokens</li><li>max: 30 tokens</li></ul> | <ul><li>min: 24 tokens</li><li>mean: 25.84 tokens</li><li>max: 28 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.56</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                         | sentence_1                                                                                                                                                                                            | label            |
  |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>I am interested in computational biology, neuroscience, and biomedical engineering. My projects focus on AI-driven applications and research systems.</code> | <code>Research interests include wireless communications, cyber-physical systems, embedded systems, and signal processing. Current work focuses on advanced interdisciplinary research.</code>        | <code>0.0</code> |
  | <code>I am interested in investment systems, data analytics, and business intelligence. My projects focus on AI-driven applications and research systems.</code>   | <code>Research interests include computer vision, recommendation systems, information retrieval, and natural language processing. Current work focuses on advanced interdisciplinary research.</code> | <code>0.0</code> |
  | <code>I am interested in sensors, circuits, and control systems. My projects focus on AI-driven applications and research systems.</code>                          | <code>Research interests include risk modeling, business intelligence, economics, and investment systems. Current work focuses on advanced interdisciplinary research.</code>                         | <code>0.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 3
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: None
- `trackio_bucket_id`: None
- `trackio_static_space_id`: None
- `per_device_eval_batch_size`: 16
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_static_graph`: None
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch | Step | rightfit-validation_average_precision |
|:-----:|:----:|:-------------------------------------:|
| 1.0   | 10   | 0.9590                                |
| 2.0   | 20   | 0.9616                                |
| 3.0   | 30   | 0.9634                                |


### Training Time
- **Training**: 52.6 seconds

### Framework Versions
- Python: 3.13.0
- Sentence Transformers: 5.5.0
- Transformers: 5.8.1
- PyTorch: 2.11.0+cu128
- Accelerate: 1.13.0
- Datasets: 4.8.5
- Tokenizers: 0.22.2

## Additional Resources

- [Training and Finetuning Reranker Models with Sentence Transformers](https://huggingface.co/blog/train-reranker): the end-to-end guide for training or finetuning Cross Encoder (reranker) models.
- [Multimodal Embedding & Reranker Models with Sentence Transformers](https://huggingface.co/blog/multimodal-sentence-transformers): use text, image, audio, and video reranker models through the same API.
- [Training and Finetuning Multimodal Embedding & Reranker Models with Sentence Transformers](https://huggingface.co/blog/train-multimodal-sentence-transformers): training multimodal Cross Encoders.

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->
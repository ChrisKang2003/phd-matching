---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:800
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
      value: 0.995
      name: Accuracy
    - type: accuracy_threshold
      value: -0.8998703956604004
      name: Accuracy Threshold
    - type: f1
      value: 0.9937888198757764
      name: F1
    - type: f1_threshold
      value: -0.8998703956604004
      name: F1 Threshold
    - type: precision
      value: 0.9876543209876543
      name: Precision
    - type: recall
      value: 1.0
      name: Recall
    - type: average_precision
      value: 0.9995312011642444
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
    ['I am interested in large language models, AI for healthcare, and computer vision. My previous projects involve applied research, data analysis, and building practical systems.', 'Dr. Cameron Moore is a faculty member at Stanford University. Research interests include AI for healthcare, recommendation systems, data mining, and cybersecurity. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.'],
    ['I am interested in platform strategy, data analytics, and market prediction. My previous projects involve applied research, data analysis, and building practical systems.', 'Dr. Kevin Garcia is a faculty member at Johns Hopkins University. Research interests include medical imaging, health informatics, wearable health devices, and drug discovery. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.'],
    ['I am interested in financial analytics, investment systems, and business intelligence. My previous projects involve applied research, data analysis, and building practical systems.', 'Dr. Leo Chen is a faculty member at Johns Hopkins University. Research interests include precision medicine, neuroscience, wearable health devices, and biomedical engineering. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.'],
    ['I am interested in computational biology, genomics, and drug discovery. My previous projects involve applied research, data analysis, and building practical systems.', 'Dr. Drew Nelson is a faculty member at University of Pennsylvania. Research interests include operations research, business intelligence, financial analytics, and marketing analytics. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.'],
    ['I am interested in circuits, wireless communications, and signal processing. My previous projects involve applied research, data analysis, and building practical systems.', 'Dr. Lina Lewis is a faculty member at University of Pennsylvania. Research interests include data analytics, operations research, financial analytics, and economics. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.'],
]
scores = model.predict(pairs)
print(scores)
# [  5.565   -9.9977 -11.0344 -11.0684 -10.6059]

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'I am interested in large language models, AI for healthcare, and computer vision. My previous projects involve applied research, data analysis, and building practical systems.',
    [
        'Dr. Cameron Moore is a faculty member at Stanford University. Research interests include AI for healthcare, recommendation systems, data mining, and cybersecurity. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.',
        'Dr. Kevin Garcia is a faculty member at Johns Hopkins University. Research interests include medical imaging, health informatics, wearable health devices, and drug discovery. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.',
        'Dr. Leo Chen is a faculty member at Johns Hopkins University. Research interests include precision medicine, neuroscience, wearable health devices, and biomedical engineering. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.',
        'Dr. Drew Nelson is a faculty member at University of Pennsylvania. Research interests include operations research, business intelligence, financial analytics, and marketing analytics. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.',
        'Dr. Lina Lewis is a faculty member at University of Pennsylvania. Research interests include data analytics, operations research, financial analytics, and economics. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.',
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
| accuracy              | 0.995      |
| accuracy_threshold    | -0.8999    |
| f1                    | 0.9938     |
| f1_threshold          | -0.8999    |
| precision             | 0.9877     |
| recall                | 1.0        |
| **average_precision** | **0.9995** |

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

* Size: 800 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 100 samples:
  |          | sentence_0                                                                         | sentence_1                                                                         | label                                                          |
  |:---------|:-----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type     | string                                                                             | string                                                                             | float                                                          |
  | modality | text                                                                               | text                                                                               |                                                                |
  | details  | <ul><li>min: 29 tokens</li><li>mean: 31.37 tokens</li><li>max: 35 tokens</li></ul> | <ul><li>min: 45 tokens</li><li>mean: 49.51 tokens</li><li>max: 53 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.39</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                        | sentence_1                                                                                                                                                                                                                                                                                             | label            |
  |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>I am interested in large language models, AI for healthcare, and computer vision. My previous projects involve applied research, data analysis, and building practical systems.</code>      | <code>Dr. Cameron Moore is a faculty member at Stanford University. Research interests include AI for healthcare, recommendation systems, data mining, and cybersecurity. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.</code>             | <code>1.0</code> |
  | <code>I am interested in platform strategy, data analytics, and market prediction. My previous projects involve applied research, data analysis, and building practical systems.</code>           | <code>Dr. Kevin Garcia is a faculty member at Johns Hopkins University. Research interests include medical imaging, health informatics, wearable health devices, and drug discovery. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.</code>  | <code>0.0</code> |
  | <code>I am interested in financial analytics, investment systems, and business intelligence. My previous projects involve applied research, data analysis, and building practical systems.</code> | <code>Dr. Leo Chen is a faculty member at Johns Hopkins University. Research interests include precision medicine, neuroscience, wearable health devices, and biomedical engineering. Recent work focuses on interdisciplinary research methods, scalable systems, and real-world applications.</code> | <code>0.0</code> |
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
| 1.0   | 50   | 0.9991                                |
| 2.0   | 100  | 0.9995                                |
| 3.0   | 150  | 0.9995                                |


### Training Time
- **Training**: 4.9 minutes

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
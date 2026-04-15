window.SAMPLES = window.SAMPLES || {};
window.SAMPLES['rag_pipeline'] = `(venv) kirankumar@192 rag % python3 rag_pipeline.py
Collection ready: my_docs
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
modules.json: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████| 349/349 [00:00<00:00, 655kB/s]
config_sentence_transformers.json: 100%|████████████████████████████████████████████████████████████████████████████████████| 116/116 [00:00<00:00, 1.68MB/s]
README.md: 10.5kB [00:00, 42.0MB/s]
sentence_bert_config.json: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 53.0/53.0 [00:00<00:00, 369kB/s]
config.json: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████| 612/612 [00:00<00:00, 4.74MB/s]
model.safetensors: 100%|████████████████████████████████████████████████████████████████████████████████████████████████| 90.9M/90.9M [00:04<00:00, 19.7MB/s]
Loading weights: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████| 103/103 [00:00<00:00, 23150.60it/s]
BertModel LOAD REPORT from: sentence-transformers/all-MiniLM-L6-v2
Key                     | Status     |  | 
------------------------+------------+--+-
embeddings.position_ids | UNEXPECTED |  | 

Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
tokenizer_config.json: 100%|████████████████████████████████████████████████████████████████████████████████████████████████| 350/350 [00:00<00:00, 3.04MB/s]
vocab.txt: 232kB [00:00, 10.5MB/s]
tokenizer.json: 466kB [00:00, 22.7MB/s]
special_tokens_map.json: 100%|███████████████████████████████████████████████████████████████████████████████████████████████| 112/112 [00:00<00:00, 860kB/s]
config.json: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████| 190/190 [00:00<00:00, 830kB/s]
Embedding model loaded.
Upserted 5 documents. Total in collection: 5

── Plain query results ─────────────────────────────────
Query: How do deep learning models train?
  [ml] score=0.550  →  Neural networks learn via backpropagation.
  [cs] score=0.114  →  Python is a dynamically typed language.

── Filtered query (source=ml) ──────────────────────────
  [ml] score=0.550  →  Neural networks learn via backpropagation.
  [ml] score=0.012  →  RAG stands for Retrieval-Augmented Generation.

── LLM prompt (RAG context injected) ──────────────────
You are a helpful assistant. Use only the context below to answer.

Context:
- Neural networks learn via backpropagation.
- Python is a dynamically typed language.

Question: How do deep learning models train?
Answer:
(venv) kirankumar@192 rag %
`;
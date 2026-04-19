window.SAMPLES = window.SAMPLES || {};
window.SAMPLES['rag_chunk_crossencoder'] = `python3 ./rag_chunk_crossencoder.py
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 103/103 [00:00<00:00, 7443.76it/s]
BertModel LOAD REPORT from: sentence-transformers/all-MiniLM-L6-v2
Key                     | Status     |  | 
------------------------+------------+--+-
embeddings.position_ids | UNEXPECTED |  | 
Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
Indexed 631 chunks
Loading weights: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 105/105 [00:00<00:00, 8694.32it/s]
BertForSequenceClassification LOAD REPORT from: cross-encoder/ms-marco-MiniLM-L-6-v2
Key                          | Status     |  | 
-----------------------------+------------+--+-
bert.embeddings.position_ids | UNEXPECTED |  | 
Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
## The Jackal And The Drum
"The Jackal And The Drum" is a story told by Damanaka to king Pingalaka to help him overcome his fear of sound (Page 5).
In the story, a hungry jackal went out searching for food and arrived at an abandoned battlefield, where he heard loud and strange sounds (Page 5). At first, he was scared and wanted to flee, but then he decided he should find out the cause of the sounds, reasoning that "whether it is fear or happiness one must know its cause" and that "such a person will never regret his actions" (Page 5).
The jackal warily followed the direction of the sounds and discovered that the source was a **drum** — the branches of a tree above were brushing against it, producing the loud noises (Page 5). Relieved, the jackal began playing the drum and thought there might be food inside it. He pierced the side of the drum to enter it but was disappointed to find no food. Still, he consoled himself by saying that he had rid himself of the fear of sound (Page 5).
The moral of the story, as applied by Damanaka, was to encourage king Pingalaka not to be afraid of sounds. After telling this tale, Damanaka sought and received the king's permission to go investigate the source of the sounds that had been troubling him (Page 5).`;
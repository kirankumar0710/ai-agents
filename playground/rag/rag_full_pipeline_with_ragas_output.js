window.SAMPLES = window.SAMPLES || {};
window.SAMPLES['rag_full_pipeline'] = `(venv) kirankumar@192 rag % python3 ./rag_full_pipeline.py
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 103/103 [00:00<00:00, 14291.83it/s]
BertModel LOAD REPORT from: sentence-transformers/all-MiniLM-L6-v2
Key                     | Status     | Details
------------------------+------------+--------
embeddings.position_ids | UNEXPECTED |        
Notes:
- UNEXPECTED:   can be ignored when loading from different task/architecture; not ok if you expect identical arch.
✅ Ingested 631 chunks
According to the context, **Panchatantra** became popular as **"children's guide in solving problems of life"** [Page 2]. The stories teach the **five strategies (Panchatantra)**, which are described as "five ways that help the human being succeed in life" [Page 1]. These five strategies are:
1. **Discord among friends**
2. **Gaining friends**
3. **Of crows and owls**
4. **Loss of gains**
5. **Imprudence**
[Page 1]
Key lessons embedded in these stories for kids include:
- The importance of **common sense** alongside learning — being very learned but without common sense makes one "the butt of ridicule" [Page 95].
- The value of **listening to friends' advice** and avoiding greed — "it is not wise to rule out the advice of a friend. Greed made you ignore my advice" [Page 98].
- That **wisdom alone without education** does not fully serve one's purpose [Page 98].
- The importance of **inclusion and sharing** — "it is not proper to send him back… Let us share our gains with him" [Page 95].
These stories were originally taught by the learned man **Sharman** to the king's sons to educate them in these life strategies, completing the task in **six months** [Page 2].
(venv) kirankumar@192 rag %`;
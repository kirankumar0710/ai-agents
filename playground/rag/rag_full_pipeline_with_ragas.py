# rag_app.py — complete minimal RAG system

import anthropic, chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
DB_CLIENT = chromadb.PersistentClient(path="./chroma_db")
PDF_FILE = "../data/the_great_panchatantra_tales_complete.pdf"


def ingest_pdf(pdf_path: str, collection_name: str = "docs"):
    reader = PdfReader(pdf_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    collection = DB_CLIENT.get_or_create_collection(collection_name)

    chunks, metas, ids = [], [], []
    for i, page in enumerate(reader.pages):
        for j, chunk in enumerate(splitter.split_text(page.extract_text() or "")):
            chunks.append(chunk)
            metas.append({"page": i + 1, "source": pdf_path})
            ids.append(f"p{i+1}_c{j}")

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=EMBED_MODEL.encode(chunks).tolist(),
        metadatas=metas,
    )
    print(f"✅ Ingested {len(chunks)} chunks")
    return collection


def ask(question: str, collection, top_k: int = 5) -> tuple[str, list[str]]:
    results = collection.query(
        query_embeddings=EMBED_MODEL.encode([question]).tolist(), n_results=top_k
    )

    # capture retrieved chunks — needed by RAGAS as "contexts"
    contexts = results["documents"][0]

    context = "\n\n".join(
        f"[Page {m['page']}] {d}"
        for d, m in zip(results["documents"][0], results["metadatas"][0])
    )
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"Answer using ONLY the context. Cite page numbers.\n\nContext:\n{context}\n\nQ: {question}",
            }
        ],
    )
    return msg.content[0].text, contexts


# Run it:
collection = ingest_pdf(PDF_FILE)
question = "What are lessons for kids?"
answer, contexts = ask(question, collection)

print(answer)

def evaluate_with_ragas(question: str, answer: str, contexts: list[str], ground_truth: str):
    # Requires: pip install ragas datasets
    # Requires: export OPENAI_API_KEY="your_api_key_here"
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from datasets import Dataset

    ragas_result = evaluate(
        Dataset.from_dict(
            {
                "question": [question],
                "answer": [answer],
                "contexts": [contexts],
                "ground_truth": [ground_truth],
            }
        ),
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    print("\n📊 RAGAS scores:")
    print(ragas_result)
    return ragas_result


# Uncomment to run RAGAS evaluation (requires OPENAI_API_KEY):
# ground_truth = (
#     "Children should be wary of help offered without clear reason, "
#     "be inclusive and share with others, accept their destiny with grace, "
#     "and fulfill responsibilities at the right time."
# )
# evaluate_with_ragas(question, answer, contexts, ground_truth)

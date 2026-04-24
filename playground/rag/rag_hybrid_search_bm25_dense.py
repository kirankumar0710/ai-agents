# What this does:
# Implements hybrid search combining BM25 (keyword) and Dense (semantic) retrieval.
# BM25 catches exact keyword matches — good for proper nouns, IDs, specific terms.
# Dense catches semantic meaning — good for synonyms, paraphrases, concepts.
# RRF (Reciprocal Rank Fusion) merges both result sets into a single ranked list.
# Neither BM25 nor Dense alone is as good as both combined.
#
# Flow:
#   query
#     → BM25 search (keyword)  → ranked list A
#     → Dense search (semantic) → ranked list B
#       → RRF fusion merges A + B by rank position
#         → top-k unique docs → LLM
#
# Example with our docs:
#   query: "Alexandr Wang Scale AI"
#   BM25  → finds "Scale AI was founded by Alexandr Wang" (exact name match)
#   Dense → finds "Scale AI provides RLHF services" (semantic context)
#   RRF   → merges both, deduplicates, returns top-k
#
# Only ANTHROPIC_API_KEY needed — BM25 is pure Python, embeddings run locally.

import os
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document

# ── Shared docs ────────────────────────────────────────────────────
# Both BM25 and Dense retrievers index the same documents.
# BM25 uses raw text. Dense uses embeddings.

docs = [
    Document(page_content="Scale AI was founded in 2016 by Alexandr Wang."),
    Document(
        page_content="Scale AI provides data labeling and RLHF services for LLMs."
    ),
    Document(page_content="GPT-4 used RLHF during its training pipeline."),
    Document(
        page_content="Anthropic was founded in 2021 by former OpenAI researchers."
    ),
    Document(
        page_content="Reinforcement learning from human feedback improves LLM alignment."
    ),
    Document(page_content="Data labeling is a core service offered by Scale AI."),
]

# ── BM25 retriever ─────────────────────────────────────────────────
# Pure keyword matching — no embeddings, no API needed.
# Works well for exact terms: names, IDs, technical keywords.
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 3  # return top 3 from BM25

# ── Dense retriever ────────────────────────────────────────────────
# Semantic embedding search — catches synonyms and related concepts.
# Runs locally via HuggingFace, no OpenAI key needed.
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(docs, embedding=embeddings)
dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ── Ensemble retriever (RRF fusion) ────────────────────────────────
# EnsembleRetriever uses Reciprocal Rank Fusion (RRF) under the hood.
# weights=[0.5, 0.5] means both retrievers contribute equally.
# Adjust weights to favour one — e.g. [0.3, 0.7] to trust dense more.
hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, dense_retriever], weights=[0.5, 0.5]
)

# ── LLM setup ─────────────────────────────────────────────────────
llm = ChatAnthropic(model="claude-sonnet-4-6")


# ── Hybrid search + answer function ───────────────────────────────
def answer_with_hybrid_search(question: str) -> str:
    print(f"\n{'='*60}")
    print(f"Question: {question}")

    # Retrieve using both BM25 + Dense, fused via RRF
    retrieved_docs = hybrid_retriever.invoke(question)

    print(f"\n[DEBUG] Retrieved {len(retrieved_docs)} docs after RRF fusion:")
    for i, doc in enumerate(retrieved_docs):
        print(f"  {i+1}. {doc.page_content}")

    # Build context from retrieved docs
    context = "\n".join(doc.page_content for doc in retrieved_docs)

    # Generate answer
    prompt = f"""Use the following context to answer the question.
If the answer is not in the context, say "I don't know based on the available documents."

Context:
{context}

Question: {question}"""

    answer = llm.invoke(prompt).content
    print(f"\nAnswer: {answer}")
    return answer


# ── Tests ──────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Test 1: Exact keyword match — BM25 shines here
    answer_with_hybrid_search("Who is Alexandr Wang?")

    # Test 2: Semantic match — Dense shines here
    answer_with_hybrid_search("What company helps align AI with human preferences?")

    # Test 3: Both contribute — hybrid wins
    answer_with_hybrid_search("What RLHF services does Scale AI offer?")

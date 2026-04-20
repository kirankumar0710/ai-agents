# Fixes the "garbage in, garbage out" problem of dense retrieval.
# Vague queries like "how does it work?" produce poor embeddings → poor retrieval.
# Claude rewrites the original query into 4 specific, vocabulary-rich variants.
# We retrieve for ALL variants and union the results — dramatically better recall.
#
# Flow:
#   original query → Claude rewrites into 4 variants
#   → retrieve k=2 docs per variant (8 total candidates)
#   → deduplicate
#   → pass unique docs to Claude for final answer
#
# Only ANTHROPIC_API_KEY needed — embeddings run locally.
#
#
# ── How query rewriting works ───────────────────────────────────────
#
# PROBLEM:
#   Vague queries like "how does it work?" produce poor embeddings
#   → poor retrieval → poor answers. Garbage in, garbage out.
#
# SOLUTION — 3 steps:
#   1. REWRITE  — Claude expands the original query into 4 specific variants.
#                 Resolves pronouns ("it", "they") if context is provided.
#                 Returns pure JSON array — no markdown.
#
#   2. RETRIEVE — Run similarity search for each variant (k=2 per variant).
#                 Union all results → deduplicate by content.
#                 More variants = better recall coverage.
#
#   3. ANSWER   — Pass all unique chunks as context to Claude.
#                 Claude answers using only the retrieved docs.
#                 If answer not in docs → says "I don't know".
#
# IMPORTANT:
#   Rewriting amplifies what's already in the query — it cannot invent context.
#   For best results, pass conversation history so Claude can resolve
#   vague pronouns like "it", "that", "they" against real subjects.
#
# FLOW:
#   original query
#     → Claude rewrites into 4 variants
#       → retrieve k=2 docs per variant  (8 total candidates)
#         → deduplicate
#           → Claude generates final answer
#
# ── Example with our docs ──────────────────────────────────────────
#
# Our vectorstore contains 4 documents:
#   "Scale AI was founded in 2016 by Alexandr Wang."
#   "Scale AI provides data labeling and RLHF services for LLMs."
#   "GPT-4 used RLHF during its training pipeline."
#   "Anthropic was founded in 2021 by former OpenAI researchers."
#
# Query: "who started the RLHF company?"
#
# Step 1 — REWRITE:
#   Claude generates 4 variants:
#   → "who founded the company that provides RLHF services"
#   → "Scale AI founder and CEO"
#   → "which company started reinforcement learning from human feedback"
#   → "RLHF data labeling startup founder"
#
# Step 2 — RETRIEVE (k=2 per variant = 8 candidates):
#   variant 1 → "Scale AI provides data labeling and RLHF services for LLMs."
#               "Scale AI was founded in 2016 by Alexandr Wang."
#   variant 2 → "Scale AI was founded in 2016 by Alexandr Wang."  ← duplicate
#               "Scale AI provides data labeling and RLHF services for LLMs."  ← duplicate
#   variant 3 → "GPT-4 used RLHF during its training pipeline."
#               "Scale AI provides data labeling and RLHF services for LLMs."  ← duplicate
#   variant 4 → "Scale AI was founded in 2016 by Alexandr Wang."  ← duplicate
#               "Scale AI provides data labeling and RLHF services for LLMs."  ← duplicate
#
#   After dedup → 3 unique chunks passed to Claude:
#   → "Scale AI was founded in 2016 by Alexandr Wang."
#   → "Scale AI provides data labeling and RLHF services for LLMs."
#   → "GPT-4 used RLHF during its training pipeline."
#
# Step 3 — ANSWER:
#   Claude reads the 3 unique chunks and answers:
#   → "Scale AI, founded by Alexandr Wang in 2016, is the company
#      that provides RLHF services used in training LLMs like GPT-4."
#
# ───────────────────────────────────────────────────────────────────

import json
from langchain_anthropic import ChatAnthropic
from tools import retrieve

llm = ChatAnthropic(model="claude-sonnet-4-6")


# ── Step 1: Query rewriter ──────────────────────────────────────────
def rewrite_query(original: str) -> list[str]:
    # Asks Claude to generate 4 distinct search variants of the original query.
    # Must return pure JSON — no markdown, no preamble — so json.loads() works.
    prompt = f"""You are a search query optimizer.

Original query: "{original}"

Generate 4 distinct search queries that would retrieve relevant documents for this question.
- Resolve any vague pronouns or references
- Add relevant technical vocabulary
- Vary the phrasing to maximize recall

Return ONLY a JSON array of strings, nothing else.
Example: ["query one", "query two", "query three", "query four"]"""

    response = llm.invoke(prompt).content
    print(f"[DEBUG] raw rewriter response: {response}")

    # Strip markdown fences if Claude wraps in ```json ... ```
    clean = (
        response.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    return json.loads(clean)


# ── Step 2: Retrieve across all variants ───────────────────────────
def retrieve_with_rewriting(question: str) -> str:
    # Rewrites into 4 variants, retrieves k=2 per variant, deduplicates.
    queries = rewrite_query(question)
    print(f"\n[DEBUG] rewritten queries:")
    for i, q in enumerate(queries):
        print(f"  {i+1}. {q}")

    all_docs = []
    for q in queries:
        # retrieve.retrieve_tool is a @tool — invoke() is the correct way to call it
        result = retrieve.retrieve_tool.invoke(q)
        all_docs.append(result)

    # Deduplicate — same chunk can be returned for multiple query variants
    seen = set()
    unique_chunks = []
    for chunk in all_docs:
        if chunk not in seen:
            seen.add(chunk)
            unique_chunks.append(chunk)

    print(f"\n[DEBUG] unique chunks after dedup: {len(unique_chunks)}")
    return "\n\n".join(unique_chunks)


# ── Step 3: Final answer using retrieved context ────────────────────
def answer_with_rewriting(question: str) -> str:
    context = retrieve_with_rewriting(question)

    prompt = f"""Use the following context to answer the question.
If the answer is not in the context, say "I don't know based on the available documents."

Context:
{context}

Question: {question}"""

    return llm.invoke(prompt).content


# ── Tests ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    questions = [
        "how does it work?",  # vague — rewriting helps a lot
        "who started the RLHF company?",  # ambiguous pronoun
        "tell me about the AI data labeling startup",  # no proper nouns
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"Original question: {q}")
        answer = answer_with_rewriting(q)
        print(f"Answer: {answer}")

import chromadb
from sentence_transformers import SentenceTransformer

# ── STEP 1: Setup — client + collection ─────────────────────
import chromadb
from sentence_transformers import SentenceTransformer

# PersistentClient saves to disk so data survives restarts.
# Swap with chromadb.Client() for a pure in-memory session.
client = chromadb.PersistentClient(path="./chroma_db")

# get_or_create means re-running the script won't crash if
# the collection already exists from a previous run.
collection = client.get_or_create_collection(
    name="my_docs", metadata={"hnsw:space": "cosine"}  # use cosine similarity
)

print("Collection ready:", collection.name)


# ── STEP 2: Embed model ──────────────────────────────────────
# all-MiniLM-L6-v2 produces 384-dimensional vectors.
# It's small, fast, and accurate enough for most RAG use-cases.
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# ── STEP 3: Documents to index ──────────────────────────────
# Each doc gets:
#   - a unique id       (used to avoid duplicates on upsert)
#   - the raw text      (stored alongside the vector)
#   - metadata dict     (used later for filtered queries)

docs = [
    "The sky is blue due to Rayleigh scattering.",
    "Python is a dynamically typed language.",
    "Neural networks learn via backpropagation.",
    "Photosynthesis converts sunlight into glucose.",
    "RAG stands for Retrieval-Augmented Generation.",
]

ids = ["doc1", "doc2", "doc3", "doc4", "doc5"]

metadatas = [
    {"source": "physics"},
    {"source": "cs"},
    {"source": "ml"},
    {"source": "biology"},
    {"source": "ml"},
]


# ── STEP 4: Embed + upsert ───────────────────────────────────
# model.encode() returns a numpy array → convert to list for Chroma.
# upsert = insert if new, update if id already exists.

embeddings = model.encode(docs).tolist()

collection.upsert(
    ids=ids,
    documents=docs,
    embeddings=embeddings,
    metadatas=metadatas,
)

print(f"Upserted {len(docs)} documents. Total in collection: {collection.count()}")


# ── STEP 5: Plain query (no filter) ─────────────────────────
# The query text is embedded with the SAME model used at index time.
# ChromaDB computes cosine similarity and returns the top-n matches.

query = "How do deep learning models train?"
query_embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=2,  # return top-2 closest docs
    include=["documents", "metadatas", "distances"],
)

print("\n── Plain query results ─────────────────────────────────")
print("Query:", query)
for doc, meta, dist in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0],
):
    print(f"  [{meta['source']}] score={1-dist:.3f}  →  {doc}")
# score = 1 - cosine_distance  (higher = more similar)


# ── STEP 6: Metadata-filtered query ─────────────────────────
# Same query, but only considers docs where source == "ml".
# Useful when your collection mixes topics and you want
# domain-scoped retrieval.

results_filtered = collection.query(
    query_embeddings=query_embedding,
    n_results=2,
    where={"source": "ml"},  # <-- the filter
    include=["documents", "metadatas", "distances"],
)

print("\n── Filtered query (source=ml) ──────────────────────────")
for doc, meta, dist in zip(
    results_filtered["documents"][0],
    results_filtered["metadatas"][0],
    results_filtered["distances"][0],
):
    print(f"  [{meta['source']}] score={1-dist:.3f}  →  {doc}")


# ── STEP 7: Use retrieved docs as LLM context (RAG pattern) ─
# This is the "augmented generation" part of RAG.
# In production you'd call OpenAI / Anthropic / Ollama here.
# Here we just print the prompt that you'd send to the LLM.

top_docs = results["documents"][0]  # plain top-2 results

context = "\n".join(f"- {d}" for d in top_docs)

prompt = f"""You are a helpful assistant. Use only the context below to answer.

Context:
{context}

Question: {query}
Answer:"""

print("\n── LLM prompt (RAG context injected) ──────────────────")
print(prompt)

# To actually call an LLM, uncomment one of these:
#
# ── Anthropic Claude ────────────────────────────────────────
# import anthropic
# client_llm = anthropic.Anthropic()
# msg = client_llm.messages.create(
#     model="claude-opus-4-6",
#     max_tokens=256,
#     messages=[{"role": "user", "content": prompt}]
# )
# print(msg.content[0].text)

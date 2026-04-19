# ── installs ──────────────────────────────────────────────
# pip install pypdf sentence-transformers chromadb langchain anthropic

# ════════════════════════════════════════════════════════════
# PHASE 1 — INDEXING  (run once, or when docs change)
# To index multiple PDFs, wrap your existing code in a loop.
#
# pdf_files = ["contract_2024.pdf", "invoice_march.pdf", "policy_hr.pdf"]
# for pdf_path in pdf_files:
#     reader = PdfReader(pdf_path)
#     ...
#     metadatas.append({"page": page_num, "source": pdf_path})
# ════════════════════════════════════════════════════════════

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# 1. Load PDF
reader = PdfReader("../data/the_great_panchatantra_tales_complete.pdf")
pages = [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]

# 2. Chunk  ← your snippet lives here
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", ".", " ", ""]
)

chunks, metadatas, ids = [], [], []
for page_num, text in pages:
    for j, chunk in enumerate(splitter.split_text(text)):
        chunks.append(chunk)
        metadatas.append({"page": page_num, "source": "doc.pdf"})
        ids.append(f"p{page_num}_c{j}")

# 3. Embed
model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim
embeddings = model.encode(chunks).tolist()

# 4. Store in ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("docs")
collection.upsert(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
print(f"Indexed {len(chunks)} chunks")

# ════════════════════════════════════════════════════════════
# PHASE 2 — QUERYING  (runs on every user request)
#
# To filter by a specific PDF, add where= to collection.query().
# The "source" value must match what was stored in metadatas above.
#
# where={"source": "contract_2024.pdf"}          # single doc
# where={"$and": [{"source": "contract_2024.pdf"},
#                 {"page": {"$gte": 5}}]}         # doc + page range
#
#
#    results = collection.query(
#        query_embeddings=q_vec,
#        n_results=10,
#        # With metadata filter — searches only matching chunks
#        # where={"source": "contract_2024.pdf"}        # single value
#        # where={"page": {"$gte": 10}}               # page range
#        # where={"$and": [{"source": "x"}, {"page": {"$lte": 5}}]
#    )
# ════════════════════════════════════════════════════════════

from sentence_transformers import CrossEncoder
import anthropic


def ask(question: str) -> str:
    # 5. Embed the query (same model — critical)
    q_vec = model.encode([question]).tolist()

    # 6. Retrieve top-10 candidates from ChromaDB
    results = collection.query(
        query_embeddings=q_vec,
        n_results=10,
        # With metadata filter — searches only matching chunks
        # where={"source": "contract_2024.pdf"}        # single value
        # where={"page": {"$gte": 10}}               # page range
        # where={"$and": [{"source": "x"}, {"page": {"$lte": 5}}]
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    # 7. Rerank — cross-encoder scores query+chunk pairs precisely
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    scores = reranker.predict([(question, d) for d in docs])
    ranked = sorted(zip(scores, docs, metas), reverse=True)

    # Keep top-3 after reranking
    top_chunks = [(d, m) for _, d, m in ranked[:3]]

    # 8. Build context and prompt Claude
    context = "\n\n".join(f"[Page {m['page']}] {d}" for d, m in top_chunks)

    prompt = f"""Answer using ONLY the context below.
Cite the page number for every claim, like (Page N).

Context:
{context}

Question: {question}"""

    response = anthropic.Anthropic().messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# Run it
print(ask("What is Jackal And The Drum"))
# → "Refunds are allowed within 30 days (Page 4).
#    Digital products are excluded (Page 7)."

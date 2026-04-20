# Turns a vector store retriever into a @tool that an agent can optionally call.
# The key idea: instead of ALWAYS retrieving, the agent decides when retrieval is needed.
# HuggingFace embeddings run locally — no OpenAI key needed.
# Only your ANTHROPIC_API_KEY is required.

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool


# Free local embeddings — no OpenAI key needed
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(embedding_function=embeddings)

# Add some docs to the vectorstore
vectorstore.add_texts(
    [
        # Hop 1 will likely retrieve these (RLHF + GPT-4 related)
        "GPT-4 used RLHF during its training pipeline.",
        "Scale AI provides data labeling and RLHF services for LLMs.",
        "Reinforcement Learning from Human Feedback (RLHF) is a technique to align AI models with human preferences.",
        "OpenAI used contractor-based human feedback pipelines to train GPT-4.",
        # Hop 2 should retrieve these (founder + Scale AI specific)
        "Scale AI was founded in 2016 by Alexandr Wang.",
        "Alexandr Wang became the world's youngest self-made billionaire after Scale AI's valuation surged.",
        "Alexandr Wang grew up in Los Alamos, New Mexico, and studied at MIT before dropping out to start Scale AI.",
        "Scale AI's early customers included Uber, Lyft, and various self-driving car companies.",
        # Noise docs — unrelated, to make retrieval non-trivial
        "Anthropic was founded in 2021 by former OpenAI researchers including Dario Amodei.",
        "Hugging Face is an AI company known for hosting open-source models and datasets.",
        "LangChain is a framework for building LLM-powered applications.",
        "ChromaDB is an open-source vector database used for semantic search.",
    ]
)


# The @tool decorator + docstring is critical —
# Claude reads the docstring to decide when to call this tool.
@tool
def retrieve_tool(query: str) -> str:
    """Search the knowledge base for relevant documents."""
    docs = vectorstore.similarity_search(query, k=4)
    return "\n\n".join(d.page_content for d in docs)

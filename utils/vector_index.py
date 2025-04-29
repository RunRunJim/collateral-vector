import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAIError
from dotenv import load_dotenv
from typing import List

load_dotenv()

# Initialize Chroma client and collection
client = chromadb.Client()
collection = client.get_or_create_collection(name="confluence_docs")

# OpenAI embedding setup
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_api_key,
    model_name="text-embedding-ada-002"
)


def split_text(text: str, chunk_size=500, overlap=50) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def index_page(doc_id: str, title: str, content: str):
    chunks = split_text(content)
    metadata = [{"source": title}] * len(chunks)

    try:
        collection.add(
            documents=chunks,
            metadatas=metadata,
            ids=[f"{doc_id}-{i}" for i in range(len(chunks))],
            embedding_function=openai_ef
        )
        print(f"✅ Indexed {len(chunks)} chunks from '{title}'")
    except OpenAIError as e:
        print(f"⚠️ OpenAI Error during indexing: {e}")


def query_index(question: str, top_k=3) -> List[str]:
    try:
        results = collection.query(
            query_texts=[question],
            n_results=top_k,
            embedding_function=openai_ef
        )
        return results['documents'][0] if results['documents'] else []
    except Exception as e:
        print(f"⚠️ Query failed: {e}")
        return []

import os
import openai
import chromadb
from chromadb.config import Settings
from utils.confluence import fetch_confluence_content
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Embedding function for OpenAI v0.28 ---
def get_openai_embeddings(texts):
    if isinstance(texts, str):
        texts = [texts]
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [d["embedding"] for d in response["data"]]

# --- Create or get Chroma collection ---
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=".chromadb"))
collection = client.get_or_create_collection(
    name="confluence_docs",
    embedding_function=get_openai_embeddings
)
def query_index(query_text, top_k=3):
    if not query_text:
        return []

    query_embedding = get_openai_embeddings(query_text)[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

# --- Indexing function ---
def index_page(confluence_url):
    from utils.confluence import extract_page_id
    page_id = extract_page_id(confluence_url)

    if not page_id:
        raise ValueError("Could not extract page ID from URL.")

    title, content, _, _, _ = fetch_confluence_content(page_id)

    if not content:
        raise ValueError("No content fetched from Confluence.")

    collection.add(
        documents=[content],
        metadatas=[{"source": confluence_url}],
        ids=[page_id]
    )

    print(f"✅ Page indexed: {title}")


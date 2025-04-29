import os
import openai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from utils.confluence import fetch_confluence_content, extract_page_id

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Define the Embedding function properly ---
class OpenAIEmbedder:
    def __init__(self):
        self.model = "text-embedding-ada-002"

    def __call__(self, input: list[str]) -> list[list[float]]:
        if isinstance(input, str):
            input = [input]
        response = openai.Embedding.create(
            model=self.model,
            input=input
        )
        embeddings = [d["embedding"] for d in response["data"]]
        return embeddings

# --- Create or get Chroma collection ---
client = chromadb.PersistentClient(path=".chromadb")
collection = client.get_or_create_collection(
    name="confluence_docs",
    embedding_function=OpenAIEmbedder()
)

# --- Querying function ---
def query_index(query_text, top_k=3):
    if not query_text:
        return []

    results = collection.query(
        query_texts=[query_text],
        n_results=top_k
    )
    return results

# --- Indexing function ---
def index_page(confluence_url):
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



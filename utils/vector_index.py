import os
import openai
import chromadb
from chromadb.config import Settings
from utils.confluence import fetch_confluence_content
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- First: define a proper embedding function class
class OpenAIEmbeddingFunction:
    def __init__(self, model="text-embedding-ada-002"):
        self.model = model

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        response = openai.Embedding.create(
            model=self.model,
            input=input
        )
        return [d["embedding"] for d in response["data"]]

# --- Then create client + collection
client = chromadb.PersistentClient(path=".chromadb")
collection = client.get_or_create_collection(
    name="confluence_docs",
    embedding_function=OpenAIEmbeddingFunction()
)

# --- Now define query function
def query_index(query_text, top_k=3):
    if not query_text:
        return []

    results = collection.query(
        query_texts=[query_text],
        n_results=top_k,
        include=["documents", "metadatas"]
    )

    documents = results.get("documents", [[]])[0]
    return documents

def show_stored_documents():
    items = collection.get()
    print(f"🔍 Found {len(items['ids'])} documents stored in collection.")
    for idx, doc_id in enumerate(items['ids']):
        print(f"{idx+1}. Document ID: {doc_id}")

# --- Indexing function
def index_page(confluence_url):
    from utils.confluence import extract_page_id
    page_id = extract_page_id(confluence_url)

    if not page_id:
        raise ValueError("Could not extract page ID from URL.")

    title, content, _, _, _ = fetch_confluence_content(page_id)

    if not content:
        raise ValueError("No content fetched from Confluence.")

    # --- ✂️ CHUNKING STEP ---
    chunk_size = 500
    chunks = []
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk.strip())

    print(f"🔹 Split into {len(chunks)} chunks")

    ids = [f"{page_id}_chunk_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        metadatas=[{"source": confluence_url, "chunk": idx} for idx in range(len(chunks))],
        ids=ids
    )

    print(f"✅ Page indexed with {len(chunks)} chunks: {title}")

if __name__ == "__main__":
    show_stored_documents()





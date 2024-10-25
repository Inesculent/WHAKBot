import os
import shutil
from langchain_chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from main import set_environment_variables

# Define the persist directory path
CHROMA_PATH = r"C:\Users\parlo\Downloads\WHaKBot\tools\chroma_db"

# Ensure the directory exists
os.makedirs(CHROMA_PATH, exist_ok=True)

def get_embedding_function():
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    return embeddings

def calculate_chunk_ids(chunks):
    # Assign unique IDs to each chunk
    for idx, chunk in enumerate(chunks):
        chunk.metadata["id"] = f"doc_{idx}"
    return chunks

def add_to_chroma(chunks: list[Document]):
    # Remove existing database for testing purposes
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"Removed existing Chroma DB at {CHROMA_PATH}")

    # Initialize Chroma
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    # Calculate Page IDs
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Fetch existing items
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"]) if "ids" in existing_items else set()
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add new documents
    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        print(f"Adding {len(new_chunks)} new documents.")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        try:
            db.add_documents(new_chunks, ids=new_chunk_ids)
            print("Documents added and DB persisted successfully.")
        except Exception as e:
            print(f"Error during add_documents or persist: {e}")
    else:
        print("No new documents to add.")

# Example usage
if __name__ == "__main__":

    set_environment_variables()
    # Create sample documents
    sample_chunks = [
        Document(page_content="Sample content 1", metadata={}),
        Document(page_content="Sample content 2", metadata={}),
    ]

    add_to_chroma(sample_chunks)
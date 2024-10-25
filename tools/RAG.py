import argparse
import os
import shutil
import logging as logger

import boto3
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from sqlconnector import open_connection, retrieve_data_rag

#from testRag import test_question
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader

from main import set_environment_variables
from pydantic import BaseModel, Field
from io import BytesIO
import PyPDF2
from numpy import float64
#__import__('pysqlite3')
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from langchain_chroma import Chroma


from langchain_openai.embeddings import OpenAIEmbeddings
import os


CHROMA_PATH = 'chroma'

def get_embedding_function():
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    return embeddings



class RetrievalAugmentedGeneration(BaseModel):
    filename: str = Field(
        description="the file name in 'data' folder that is most appropriate for the task requested"
    )
    context: str = Field(
        description="the user input that was given"
    )

class SQL_RAG(BaseModel):
    context: str = Field(
        description="The user input that was given, worded in the most efficient manner to search a vectorized database"
    )

def inspect_sample_chunks(chunks):
    for idx, chunk in enumerate(chunks[:3]):  # Inspect first 3 for brevity
        print(f"Chunk {idx}:")
        print(f"  Page Content: {chunk.page_content[:100]}")  # First 100 chars
        print(f"  Metadata: {chunk.metadata}")
        print("-" * 40)


def validate_and_sanitize_chunks(chunks, max_length=5000):
    """Validate and sanitize chunks before adding to ChromaDB."""
    valid_chunks = []
    invalid_chunks = []
    for idx, chunk in enumerate(chunks):
        valid = True
        reasons = []

        # Validate page_content
        if not isinstance(chunk.page_content, str):
            valid = False
            reasons.append("page_content is not a string.")
        elif not chunk.page_content.strip():
            valid = False
            reasons.append("page_content is empty or whitespace.")
        elif len(chunk.page_content) > max_length:
            # Optionally, split or skip
            original_length = len(chunk.page_content)
            chunk.page_content = chunk.page_content[:max_length]
            logger.warning(
                f"Chunk {chunk.metadata.get('id')} truncated from {original_length} to {max_length} characters.")

        # Validate metadata
        if not isinstance(chunk.metadata, dict):
            valid = False
            reasons.append("metadata is not a dict.")
        else:
            if "id" not in chunk.metadata:
                valid = False
                reasons.append("metadata missing 'id'.")
            elif not isinstance(chunk.metadata["id"], str):
                valid = False
                reasons.append("'id' in metadata is not a string.")

        if valid:
            valid_chunks.append(chunk)
        else:
            invalid_chunks.append((idx, reasons))

    return valid_chunks, invalid_chunks


@tool("RAG", args_schema=RetrievalAugmentedGeneration)
def RAG_TOOL(filename: str, context: str) -> list[tuple[Document, float64]]:
    """When you get a request for info that may be stored in a pdf in file 'data' you use this tool to retrieve info from the appropriate pdf file
    From there, provide the context (user question) to the tool so that it may process it"""
    set_environment_variables("WHaK AI")

    s3 = boto3.client('s3')
    bucket = 'rag-pdf-storage'


    print("This is the file utilized: " + filename)

    pdf_stream = BytesIO()
    s3.download_fileobj(bucket, filename, pdf_stream)

    pdf_reader = PyPDF2.PdfReader(pdf_stream)
    pdf_text = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_text += page.extract_text()

    documents = [Document(page_content=pdf_text)]


    print("here5")
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()
    # Create (or update) the data store.
    chunks = split_documents(documents)
    add_to_chroma(chunks)

    embedding_function = get_embedding_function()

    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(context, k=5)
    return results

@tool("SQL_RAG", args_schema=SQL_RAG)
def SQL_RAG(context: str) -> list[tuple[Document, float64]]:
    """Search SQL database to get potential answer. This is extremely useful in scenarios where context by the user is not provided, or when
    you need to reference a previous conversation that has been saved"""

    set_environment_variables("WHaK AI")


    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")




    # Create (or update) the data store.
    documents = load_documents_rag()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

    embedding_function = get_embedding_function()

    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(context, k=5)

    db.reset_collection()

    return results


    #use rag_tool and C:\Users\parlo\Downloads\WHaKBot\tools\data\02_Laws_of_Logic.pdf to answer "Truth tables run out of usefulness very quickly when working with"

   ##    documents = load_documents()
def load_documents_rag():
    conn = open_connection()  # Update this to your database
    documents = retrieve_data_rag(conn)
    conn.close()  # Close the connection after retrieving data
    return documents

def load_documents():
  document_loader = PyPDFDirectoryLoader('data')
  return document_loader.load()

def inspect_chunk_types(chunks):
    for idx, chunk in enumerate(chunks[:5]):  # Inspect first 5 for brevity
        print(f"Chunk {idx}: Type - {type(chunk)}")


   
def add_to_chroma(chunks: list[Document]):
    # Load the existing database.


    #if os.path.exists(CHROMA_PATH):
        #shutil.rmtree(CHROMA_PATH)

    db = Chroma(
persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    print(dir(db))

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
          new_chunks.append(chunk)



    if len(new_chunks):
        print(f"Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]


        try:
            db.add_documents(new_chunks, ids = new_chunk_ids)
        except Exception as e:
            print(f"Error during adding documents: {e}")

        #print("Here1")
        #db.add_documents(new_chunks, ids=new_chunk_ids) #error
    else:
        print("No new documents to add")

def save_to_chroma(chunks: list[Document]):
    # Clear out the existing database directory if it exists
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new Chroma database from the documents using OpenAI embeddings
    print("WHAK")
    db = Chroma.from_documents(
        chunks,
        get_embedding_function(),
        persist_directory=CHROMA_PATH
    )

    print("HERE")
    # Persist the database to disk
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")
        

def calculate_chunk_ids(chunks):

# Page Source : Page Number : Chunk Index
    
    last_page_id = None
    current_chunk_index = 0
    
    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"
    
        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
    
        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
    
        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id
    
    return chunks


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=128   ,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


#if __name__ == '__main__':
    #faulthandler.enable()
    #RAG_TOOL("d6m3G9_Fundamentals_of_Digital_Logic_with_Verilog_Design.pdf", "We can use 2 four-variable maps to construct a?")




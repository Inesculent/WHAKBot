#Changed from Bedrock to Ollama cause of some error, will have to figure out later
#from langchain_community.embeddings.ollama import OllamaEmbeddings
#from chromadb.utils import embedding_functions
#from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings
#from langchain_huggingface import HuggingFaceEmbeddings
import os




def get_embedding_function():
    #embeddings = BedrockEmbeddings(client = any, credentials_profile_name="default", region_name="us-east-1")
    #embeddings = OllamaEmbeddings(model="nomic-embed-text")
    #embeddings = OpenAIEmbeddings()
    #embeddings = embedding_functions.DefaultEmbeddingFunction()
    #embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


    embeddings = OpenAIEmbeddings(openai_api_key= os.getenv("OPENAI_API_KEY"))
    return embeddings



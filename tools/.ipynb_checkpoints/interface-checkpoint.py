import argparse
from langchain_community.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from backup import get_embedding_function
from langchain import HuggingFaceHub, LLMChain


CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def main():
  # Create CLI.
  parser = argparse.ArgumentParser()
  parser.add_argument("query_text", type=str, help="The query text.")
  args = parser.parse_args()
  query_text = args.query_text
  query_rag(query_text)


def query_rag(query_text: str):
  # Prepare the DB.
  embedding_function = get_embedding_function()
  
  db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

  # Search the DB.
  results = db.similarity_search_with_score(query_text, k=5)

  context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
  prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
  prompt = prompt_template.format(context=context_text, question=query_text)
  #print(prompt)
 #Mistral-7B-Instruct-v0.1
  #model = Ollama(model="mistral")
  input_dict = {
      "context": "you are a tool in a larger langgraph agent, summarize the important info so that a smarter model can interpret that to give to the user: " + context_text,  # The combined document content
      "question": query_text    # The user's question
  }
  model = LLMChain(prompt=prompt_template, 
    llm=HuggingFaceHub(repo_id="mistralai/Mistral-7B-Instruct-v0.3",
                      model_kwargs={"temperature":1, 
                                    "max_length":64}, huggingfacehub_api_token='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'))
  
  #response_text = model.invoke(prompt)
  response_text = model.run(input_dict)

  print(response_text)

  #sources = [doc.metadata.get("id", None) for doc, _score in results]
  ##formatted_response = f"Response: {response_text}\nSources: {sources}"
  #print(formatted_response)
  return response_text


if __name__ == "__main__":
  main()
  
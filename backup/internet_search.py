import uuid
from pathlib import Path
import requests
import json
from langchain.tools import tool
from pydantic import BaseModel, Field

# Assuming you have an API key for a search engine or a custom API for searching the web.
CLIENT = requests.Session()
CLIENT.headers.update({"Authorization": "Bearer your_api_key_here"})


class WebSearchInput(BaseModel):
    query: str = Field(
        description="The search query to find information on the web."
    )


@tool("web_search", args_schema=WebSearchInput)
def web_search(query: str) -> dict:
    """Search the web and return results based on the specified query."""
    url = "https://your-search-api.com/api/search"
    response = CLIENT.get(url, params={"q": query})

    try:
        response.raise_for_status()  # Ensures we handle HTTP errors.
        search_results = response.json()  # Converts the response to JSON.
        return search_results  # You might want to format this depending on your needs.
    except requests.RequestError as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Failed to decode response."}

# Example usage within the same script:
# if __name__ == "__main__":
#     results = web_search.run(query="latest news on technology")
#     print(results)

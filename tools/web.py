import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from pydantic import BaseModel, Field
import json
def parse_html(html_content: str) -> str:
    """Parses HTML content and extracts cleaned text."""
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in ["nag", "footer", "aside", "script", "style", "img", "header"]:
        for match in soup.find_all(tag):
            match.decompose()  # removes all matched tags
    text_content = soup.get_text()
    text_content = " ".join(text_content.split())
    return text_content[:8_000]

def get_webpage_content(url: str) -> str:
    """Fetches webpage content and parses it to plain text."""
    response = requests.get(url)
    html_content = response.text
    text_content = parse_html(html_content)
    print(f"URL: {url} - fetched successfully")
    return text_content

class ResearchInput(BaseModel):
    research_urls: list[str] = Field(description="Must be a valid list of URLs.")

@tool("research", args_schema=ResearchInput)
def research(research_urls: list[str]) -> str:
    """Gets content of provided URLs for research purposes."""
    contents = [get_webpage_content(url) for url in research_urls]
    return json.dumps(contents)

# Example Usage:
# if __name__ == "__main__":
#     research_instance = ResearchInput(research_urls=["http://example.com"])
#     results = research(research_urls=research_instance.research_urls)
#     print(results)

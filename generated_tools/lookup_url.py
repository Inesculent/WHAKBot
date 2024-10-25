
# Retain original import statements (if any), and append the following imports
from pydantic import BaseModel, Field
from langchain.tools import tool

# Define a class for arguments
class LookupURLArgs(BaseModel):
    url: str = Field("The web URL to look up")

# Decorate the function with @tool
@tool("lookup_url", args_schema=LookupURLArgs)
def lookup_url(url:str)->str:
    """
    Look up the content of a specified web URL and return the HTML as a string.
    """
    import requests
    response = requests.get(url)
    return response.text

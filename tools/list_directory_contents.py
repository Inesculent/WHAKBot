
# IMPORTANT: Retain original import statements (if any), and append the following imports
from pydantic import BaseModel, Field
from langchain.tools import tool

# Define a class for arguments
class ListDirectoryContentsArgs(BaseModel):
    directory_path: str = Field("The path of the directory to list contents from")

# Decorate the function with @tool
@tool("list_directory_contents", args_schema=ListDirectoryContentsArgs)
def list_directory_contents(directory_path):
    """
    List all contents in the specified directory.
    """
    import os
    try:
        contents = os.listdir(directory_path)
        return contents
    except Exception as e:
        return str(e)

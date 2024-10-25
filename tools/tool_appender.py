from langchain_core.tools import tool
from pydantic import BaseModel, Field
import os
import importlib.util
import sys
import re
import ast
import subprocess


def extract_function_name_from_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            tool_code = file.read()  # Read the entire file content

        # Enhanced regex to find the function name
        match = re.search(r'^\s*def\s+(\w+)\s*\(', tool_code, re.MULTILINE)
        if match:
            return match.group(1)
        else:
            raise ValueError("No function definition found in the specified file.")
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} was not found.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")


def has_docstring_in_file(file_path: str) -> bool:
    """Check if any function or class in the given Python file has a docstring."""
    with open(file_path, 'r') as file:
        file_contents = file.read()

    # Parse the file contents into an Abstract Syntax Tree (AST)
    tree = ast.parse(file_contents)

    # Check for docstrings in functions and classes
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node):
                return True  # A docstring is found


class append_tool(BaseModel):

    classMaker: str = Field(
    '''
# Retain original import statements (if any), and append the following imports
from pydantic import BaseModel, Field
from langchain.tools import tool

# Define a class for arguments
class {name_of_class}(BaseModel):
    {for each argument}: {type of argument} = Field("Describe the argument")

# Decorate the function with @tool
@tool("{name_of_the_function}", args_schema={name_of_class})
def {function_name}({arguments}):
    
    # (Important) Add a docstring here describing what the function does
    
    # Insert the code here
    '''
    )
    file_name: str = Field(
        "Pass the filename of the tool that you created"
    )


@tool("append_to_self", args_schema=append_tool)

def append_to_self(file_name, classMaker):
    """
    Append a tool to yourself only if the user intends to create it.
    """


    file_write = 'generated_tools/' + file_name
    file_read = 'generated_functions/' + file_name
    print("Appending" + classMaker)


    tool_function = extract_function_name_from_file(file_read)

    try:
        # Open the file in write mode to overwrite the content
        with open(file_write, 'w') as file:
            # Write the new code to the file, replacing all existing content
            file.write(classMaker)

    except IOError as e:
        print(f"Error writing to file {file_write}: {e}")
        return "Failed to write to the file."

    if not has_docstring_in_file(file_write):
        return "Error, the file doesn't have a docstring, please try appending again with the necessary arguments"

    file_path_raw = file_name.replace(".py", "")
    tool_entry = f"generated_tools.{file_path_raw}:{tool_function}"
    print("Currently here!!!")
    try:
        with open('generated_tools.txt', "a") as file:
            if file.tell() != 0:  # If not empty, add a newline before writing
                file.write("\n")

            print("Currently here!")
            file.write(tool_entry)
            print(f"Tool appended successfully: {tool_entry.strip()}")
    except IOError as e:
        print(f"Error writing to file {file_name}: {e}")


    return "Successfully appended to the file."


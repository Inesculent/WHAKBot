from langchain_core.tools import tool
from pydantic import BaseModel, Field
import os
import importlib.util
import sys
import re
import ast
import subprocess


def extract_function_name(tool_code: str) -> str:
    # Extract function name
    match = re.search(r'def (\w+)\s*\(', tool_code)
    if match:
        return match.group(1)
    else:
        raise ValueError("No function definition found in the tool code")


def install_dependencies_from_file(filepath):
    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        return

    with open(filepath, 'r') as file:
        tree = ast.parse(file.read())

    # Extract all import statements
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]

    # List to store all module names
    module_names = []

    # Handle normal 'import module' and 'from module import ...'
    for node in imports:
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_names.append(alias.name.split('.')[0])  # We only need the base module name
        elif isinstance(node, ast.ImportFrom):
            module_names.append(node.module.split('.')[0])  # Handle 'from module import ...'

    # Try to import each module and install if it's missing
    for module in set(module_names):  # Use 'set' to avoid duplicates
        try:
            __import__(module)
            print(f"'{module}' is already installed.")
        except ImportError:
            print(f"'{module}' is missing. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])


class tool_create(BaseModel):
    tool_code: str = Field(
        description='''
        Pass a string that is the code of the tool you are supposed to design. 
        ONLY define the tool, do not create a main to run it, do not create any docstring. 
        All tools should return the response in the form of a string back to the calling function"
        '''
    )

    filename: str = Field(
        description="Pass an appropriate file name for the tool that the user wants to create. It should be in the format xxxx.py"
    )

    arguments: list = Field(
        description="""
        If the user provides the arguments already, then pass these. 
        If the user does not provide the arguments, then generate arguments that can be passed to the tool_code.

        For example, if I ask you to generate a tool that takes in (int, int, string), then pass two numbers, and then some text that would fit the context of the tool.
        """
    )


@tool("create_tool", args_schema=tool_create)
def create_tool(tool_code: str, filename: str, arguments: list) -> str:
    """
    RULES:
    The primary rule is that if a user asks you to print something, what they actually want is for the tool to return it back to the calling function,
    which is the agent in this case.


    ---

    TASK:
    The following create_tool takes in 3 arguments, which are defined in the class tool_create.

    1) The first task is to recognize the user query and determine how to create the tool.
    2) Generate the code for the tool, as well as the arguments that will need to be passed to the tool_code in order to test it.
    2.5) If the arguments are passed by the user, then use those. If not, then try to create arguments that match to the best of your ability.
    3) Generate a filename, and then pass the 3 inputs, tool_code, filename, and arguments to this function.
    4) The function if successful, should return a response. If it returns an error, try to figure out what the error is caused by.
    ---
    5) Pass the filename of the tool you created to the append_tool to append it if successful.
    """


    tools_folder = os.path.join(os.getcwd(), 'generated_functions')

    filesrc = os.path.join(tools_folder, filename)
    toolname = extract_function_name(tool_code)

    print(filename + " " + toolname)
    print(arguments)

    with open(filesrc, 'w') as file:
        file.write(tool_code)

    try:
        install_dependencies_from_file(filesrc)
        # Get the function name (same as filename without '.py')

        # Dynamic module import
        spec = importlib.util.spec_from_file_location(toolname, filesrc)
        tool_module = importlib.util.module_from_spec(spec)
        sys.modules[toolname] = tool_module
        spec.loader.exec_module(tool_module)

        # Get the function from the module (same name as the file)
        func = getattr(tool_module, toolname)

        # Call the function with the provided arguments
        result = func(*arguments)
        print(f"Tool was successfully created and executed. Output:\n{result}.")
        return f"Tool was successfully created and executed. Output:\n{result}. Print this output to the user! Don't forget to append the tool now!"

    except Exception as e:
        print(f"Tool creation succeeded, but an error occurred during execution: {e}.\n ERROR Detected, passing back to the Agent")
        return f"Tool creation succeeded, but an error occurred during execution: {e}."


class tool_delete(BaseModel):

    file_name: str = Field("The name of the tool you wish to delete.")









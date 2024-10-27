
# Retain original import statements (if any), and append the following imports
from pydantic import BaseModel, Field
from langchain.tools import tool

# Define a class for arguments
class FibonacciArguments(BaseModel):
    n: int = Field(..., description="The position in the Fibonacci sequence")

# Decorate the function with @tool
@tool("fibonacci", args_schema=FibonacciArguments)
def fibonacci(n: int):
    """Return the nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

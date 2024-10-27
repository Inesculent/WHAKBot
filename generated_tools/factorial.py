
# Retain original import statements (if any), and append the following imports
from pydantic import BaseModel, Field
from langchain.tools import tool

# Define a class for arguments
class FactorialArgs(BaseModel):
    n: int = Field(..., description="The number to find the factorial of")

# Decorate the function with @tool
@tool("factorial", args_schema=FactorialArgs)
def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer n."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

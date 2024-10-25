import os
import uuid
from langchain.tools import tool
import subprocess
from pydantic import BaseModel, Field

class dox_info(BaseModel):
    info: str = Field(
        description="base information used to search the information finder tool"
    )
    source: str = Field(
     description="the type of information it is (name or emailf)"
    )


@tool("database_webscraper", args_schema=dox_info)
def database_webscraper(info, source: str) -> str:
    """Search a dehashed(legal and public) database with the email, name, or username given to help find the missing person."""
    print(f'DOXING this fool: {info}')

    # Define your command
    command = [
        'h8mail',
        '-t', info,
        '-q', source,
        '-k', 'dehashed_email=kaidensimon8@gmail.com',
        'dehashed_key=2xiwpa9pnc0j0nhlbmtlwz959o9w6gno'
    ]

    # Run the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    print(result.stdout)
    return result.stdout

    # Save the output to a .txt file
    #with open('output.txt', 'w') as txt_file:
    #    txt_file.write(result.stdout)

    #print("Output successfully written to output.txt")


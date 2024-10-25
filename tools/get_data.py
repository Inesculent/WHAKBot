from langchain.tools import tool
import mysql.connector
from pydantic import BaseModel, Field


class GetDatabaseInformation(BaseModel):
    database_description: str = Field(
        description="Get all the previous user inputs and agent responses from a SQL database"
    )



@tool("get_data", args_schema=GetDatabaseInformation)
def get_data() -> str:
    """No input is required. Use the data returned from the SQL database to formulate a response if necessary"""
    conn = mysql.connector.connect(
        host="database-1.cxaqcs0sejmd.us-east-1.rds.amazonaws.com",
        user="admin",
        password="AmazonSucks$1",
        database="user_data"
    )
    cursor = conn.cursor()


    cursor.execute("SELECT user_query, agent_response FROM user_inputs")
    rows = cursor.fetchall()

    tuple_strings = ['(%s, %s)' % t for t in rows]
    result = ', '.join(tuple_strings)
    cursor.close()

    return result

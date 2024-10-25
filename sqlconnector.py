import mysql.connector
from langchain_core.documents import Document
import os


def open_connection():


  conn = mysql.connector.connect(
    host="database-1.cxaqcs0sejmd.us-east-1.rds.amazonaws.com",
    user="admin",
    password= os.getenv("AWS_PASSWORD"),
    database="user_data"
  )

  cursor = conn.cursor()

  cursor.execute('''
  CREATE TABLE IF NOT EXISTS user_inputs (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_query TEXT NOT NULL,
      agent_response TEXT NOT NULL
  )
  ''')

  cursor.close()

  return conn


def insert_data(conn, user_input, llm_response):

  cursor = conn.cursor()
  sql = "INSERT INTO user_inputs (user_query, agent_response) VALUES (%s, %s)"
  values = (user_input, llm_response)
  cursor.execute(sql, values)
  conn.commit()
  print(f"Inserted {cursor.rowcount} row(s) into the database.")

  cursor.close()

def describe(conn):
  cursor = conn.cursor()
  cursor.execute("DESCRIBE user_inputs")

  table_description = cursor.fetchall()

  for row in table_description:
    print(row)

  cursor.close()

def retrieve_data_rag(conn):
  cursor = conn.cursor()
  cursor.execute("SELECT user_query, agent_response FROM user_inputs")
  rows = cursor.fetchall()
  documents = []  # Initialize a list to hold Document instances

  for row in rows:
    user_query = row[0]
    agent_response = row[1]

    # Create a Document instance for each row
    document = Document(page_content=user_query, metadata={"agent_response": agent_response})
    documents.append(document)

  cursor.close()
  return documents

def retrieve_data(conn):
  cursor = conn.cursor()
  cursor.execute("SELECT user_query, agent_response FROM user_inputs")
  rows = cursor.fetchall()
  for row in rows:
    print(f"user_query: {row[0]}, agent_response: {row[1]}")

  cursor.close()


def retrieve_data_type(conn, type):
  cursor = conn.cursor()
  cursor.execute(f"SELECT {type} FROM user_inputs")
  rows = cursor.fetchall()
  for row in rows:
    print(row[0])

  cursor.close()


def delete_all(conn):
  cursor = conn.cursor()
  delete_all_query = "DELETE FROM user_inputs"

  # Execute the query
  cursor.execute(delete_all_query)

  # Commit the changes
  conn.commit()

  print(f"{cursor.rowcount} record(s) deleted.")

  cursor.close()

def delete_table(conn, table_name):

  cursor = conn.cursor()
  delete_table_query = f"DROP TABLE IF EXISTS {table_name}"

  cursor.execute(delete_table_query)

  conn.commit()

  print("Table dropped successfully.")
  cursor.close()

def close_connection(conn):
  conn.close()


#if __name__ == "__main__":

  #conn = open_connection()
  #retrieve_data(conn)
  #close_connection(conn)


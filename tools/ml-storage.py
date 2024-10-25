import sqlite3
import boto3



def uploadDbFile(input_text: str, file_location: str, input_type: str, table_name: str) -> str:

    s3 = boto3.resource('s3')



    con = sqlite3.connect(file_location)

    cur = con.cursor()

    listOfTables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name= ?",(input_type,))

    if listOfTables == []:

        cur.execute("CREATE TABLE llm_gen(type, text)")

        cur.execute("INSERT INTO llm_gen(type, text) VALUES (?, ?)", (input_type, input_text))



    else:
        cur.execute("INSERT INTO llm_gen(type, text) VALUES (?, ?)", (input_type, input_text))


    res = cur.execute("SELECT text FROM llm_gen")

    print(listOfTables.fetchall())

    con.commit()





if __name__ == '__main__':
    uploadDbFile('my name is van nyshadham 334', '../backup/movie.db', "user_input", "llm_gen")
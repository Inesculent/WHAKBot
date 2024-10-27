import boto3
import botocore.exceptions
import json
import os


def updateDatabase(text: str, file_location: str, input_type: str) -> str:

    #json_new = s3.Object(bucket, "storage_file.json")

    #file_content = json_new.get()['Body'].read().decode('utf-8')

    #json_content = json.loads(file_content)

    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                      )
    bucket = 'llm-output-generated'

    try:
        json_new = s3.Object(bucket, file_location)

        file_content = json_new.get()['Body'].read().decode('UTF-8')



        json_content = json.loads(file_content)

        print(json_content)


        new_json = {"message_type": input_type, "outputs": text}

        json_content["arguments"].append(new_json)

        json_new.put(
            Body=(bytes(json.dumps(json_content, indent=4).encode('UTF-8')))
        )



    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":

            json_content = {"arguments": []}

            new_json = {
                "arguments": [
                    {"message_type": input_type, "outputs": text}
                ]
            }

            json_content['arguments'].extend(new_json['arguments'])

            input_file = json.dumps(new_json)

            s3object = s3.Object(bucket, file_location)

            s3object.put(
                Body=(bytes(json.dumps(input_file, indent=4).encode('UTF-8')))
            )

        else:
            print("Error updating database" + e.response['Error']['Code'])


def retriveDatabase(file_location: str, input_type: str) -> str:
    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                      )
    bucket = 'llm-output-generated'

    try:
        json_new = s3.Object(bucket, file_location)

        file_content = json_new.get()['Body'].read().decode('UTF-8')

        json_content = json.loads(file_content)

        print(json_content)
        return "Success"
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":

            print("No file found in database")
        else:
            print("Error in database" + e.response['Error']['Code'])


#if __name__ == '__main__':
    #updateDatabase("brhuh", "storage_file.json", "inputs")

    #retriveDatabase("storage_file.json", "inputs")
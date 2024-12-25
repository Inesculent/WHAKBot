import boto3
import time
import os

def upload_to_aws(filename: str) -> str:


    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                      )
    bucket = 'llm-output-generated'

    timestr = time.strftime("%Y%m%d-%H%M%S")
    key_name = f'{timestr}-{filename}'

    s3.upload_file(filename, bucket, key_name)

    url = s3.generate_presigned_url('get_object',
                                    Params={
                                        'Bucket': 'llm-output-generated',
                                        'Key': key_name,
                                    },
                                    ExpiresIn=3600)
    return url



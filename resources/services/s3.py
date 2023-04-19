import re
import boto3

from collections import Counter

client = boto3.client('s3')

def getBucketObjects(bucket_name, max_keys):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_objects_v2.html
    response = client.list_objects_v2(
        Bucket=bucket_name,
        MaxKeys=max_keys,
    )
    
    # Getting filenames from the object
    files = []
    for i in response['Contents']:
        files.append(i['Key'])
    
    return files


def readFileContents(bucket_name, file_name):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html#
    # https://www.radishlogic.com/aws/boto3/how-to-read-a-file-in-s3-and-store-it-in-a-string-using-python-and-boto3/
    response = client.get_object(
        Bucket=bucket_name,
        Key=file_name,
    )
    
    body = response.get('Body')
    bytes_text = body.read()
    
    # Converting bytes to string
    text = bytes_text.decode()
    
    return text


def countWordsFrequency(text):
    # Extracting words only and ignoring special characters
    words = re.findall('\w+', text)
    
    words_freq = Counter(words)
    string = ''
    
    # Constructing string to prettify result
    for k, v in words_freq.items():
        t = 'times' if v > 1 else 'time'
        string += f'\'{k}\' appeared {v} {t}\n'
        
    return string


def writeToFileInS3(bucket_name, file_name, text):
    # Converting string to binary format
    binary_text = text.encode('utf-8')
    
    # https://stackoverflow.com/a/40336919
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html
    response = client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=binary_text
    )
    
    if response:
        return True
    return False
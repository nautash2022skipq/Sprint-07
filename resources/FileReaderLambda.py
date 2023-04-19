from services.s3 import (
    getBucketObjects, 
    readFileContents, 
    countWordsFrequency,
    writeToFileInS3
)
from services.sns import sendEmail

BUCKET_NAME = 'nautashahmaddesignproblem05bucket'

def lambda_handler(event, context):
    # Getting files from S3 bucket
    files = getBucketObjects(bucket_name=BUCKET_NAME, max_keys=10)

    # Creating list of strings
    # Each string will have filename, file contents and words frequency
    data = []
    for file in files:
        content = readFileContents(bucket_name=BUCKET_NAME, file_name=file)
        frequency = countWordsFrequency(text=content)
        
        string = f'Filename: {file}\n' + '-' * 30 + f'\nContent: {content}\n' + '-' * 30 + '\n' + frequency + '\n'
        data.append(string)
        
    # Creating string to write to file on S3 bucket
    output_string = ''
    for d in data:
        output_string += d + '\n\n\n'
    
    # Writing to file in S3 bucket
    response = writeToFileInS3(bucket_name=BUCKET_NAME, file_name='output/output.txt', text=output_string)
    
    if not response:
        raise Exception('Couldnot write to file in S3')
    
    messageId = sendEmail(
        recipient='nautash.ahmad.skipq@gmail.com', 
        subject='AWS Lambda files content and their words frequency', 
        message=output_string
    )
    
    if not messageId:
        raise Exception('Couldnot send email')
    else:
        print(f'Email sent with messageId {messageId}')
    
    return data
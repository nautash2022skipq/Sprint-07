import os
import json
import boto3

from ApiGatewayHandler import formatJSONResponse

client = boto3.client('s3')

def lambda_handler(event, context):
    # https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html
    path = event['path']
    httpMethod = event['httpMethod']
    
    bucket_name = os.environ['s3bucketName']
    
    print(f'Bucket: {bucket_name}')
    print(f'Path: {path} ------- httpMethod: {httpMethod}')
    
    if path == '/upload' and httpMethod == 'GET':
        try:
            queryStringParameters = event['queryStringParameters']
            if not queryStringParameters:
                raise Exception('queryStringParameters not found')
            
            key = queryStringParameters['file']
            
            # Expires in 10 mins
            expiresIn = 10 * 60
            
            params = {
                'Bucket': bucket_name,
                'Key': key
            }
            
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_url.html
            # https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html
            url = client.generate_presigned_url(ClientMethod='put_object', Params=params, ExpiresIn=expiresIn)
            
            print(url)
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': url
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
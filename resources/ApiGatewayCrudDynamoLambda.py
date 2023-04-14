import os
import json
import boto3

from ApiGatewayHandler import formatJSONResponse, generateAlphanumericID

dynamo = boto3.resource('dynamodb', 'us-east-2')
table = dynamo.Table(os.environ['tableName'])

def lambda_handler(event, context):
    # https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html
    path = event['path']
    httpMethod = event['httpMethod']
    
    print(f'Path: {path} ------- httpMethod: {httpMethod}')
    
    if path == '/url-01' and httpMethod == 'POST':
        try:
            body = json.loads(event['body'])
            url = body['url']
            
            # https://dynobase.dev/dynamodb-python-with-boto3/#put-item
            data = table.put_item(
                Item={
                    'id': generateAlphanumericID(8),
                    'url': url
                }
            )
            print(data)
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': data
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
            
    elif path == '/url-02' and httpMethod == 'POST':
        try:
            body = json.loads(event['body'])
            url = body['url']
            
            # https://dynobase.dev/dynamodb-python-with-boto3/#put-item
            data = table.put_item(
                Item={
                    'id': generateAlphanumericID(8),
                    'url': url
                }
            )
            print(data)
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': data
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
            
    elif path == '/url-03' and httpMethod == 'POST':
        try:
            body = json.loads(event['body'])
            url = body['url']
            
            # https://dynobase.dev/dynamodb-python-with-boto3/#put-item
            data = table.put_item(
                Item={
                    'id': generateAlphanumericID(8),
                    'url': url
                }
            )
            print(data)
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': data
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
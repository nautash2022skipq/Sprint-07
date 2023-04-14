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
    queryStringParameters = event['queryStringParameters']
    
    print(f'Path: {path} ------- httpMethod: {httpMethod}')
    
    if path == '/testUrls' and httpMethod == 'GET' and not queryStringParameters:
        try:
            # https://dynobase.dev/dynamodb-python-with-boto3/#scan
            data = table.scan()['Items']
            print(f'Scanned {data}')
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': data
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
        
    elif path == '/testUrls' and httpMethod == 'GET' and queryStringParameters:
        try:
            id = queryStringParameters['id']
            
            # https://dynobase.dev/dynamodb-python-with-boto3/#get-item
            data = table.get_item(
                Key={
                    'id': id
                }
            )
            print(f'Item {data}')
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': data
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
        
    elif path == '/testUrls' and httpMethod == 'POST':
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
        
    elif path == '/testUrls' and httpMethod == 'PUT':
        try:
            body = json.loads(event['body'])
        
            id = body['id']
            url = body['url']
            
            # https://dynobase.dev/dynamodb-python-with-boto3/#update-item
            # DynamoDB reserved keywords: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ReservedWords.html
            # Reserved keyword error fix: https://stackoverflow.com/questions/48653365/update-attribute-timestamp-reserved-word
            data = table.update_item(
                Key={
                    'id': id,
                },
                UpdateExpression='SET #updateUrl = :newUrl',
                ExpressionAttributeValues={
                    ':newUrl': url
                },
                ExpressionAttributeNames={
                    '#updateUrl': 'url'
                },
                ReturnValues='UPDATED_NEW'
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
        
    elif path == '/testUrls' and httpMethod == 'DELETE' and queryStringParameters:
        try:
            id = queryStringParameters['id']
            
            # https://dynobase.dev/dynamodb-python-with-boto3/#delete-item
            data = table.delete_item(
                Key={
                    'id': id
                }
            )
            print(f'Item {data}')
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': data
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
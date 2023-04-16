import os
import json
import time
import boto3

from datetime import datetime, timedelta
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
            data = body['data']
            
            items = getListOfItems(data)
                
            # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#batch-writing
            with table.batch_writer() as writer:
                for item in items:
                    writer.put_item(Item=item)
            print(items)
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': items
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
            
    elif path == '/url-02' and httpMethod == 'POST':
        try:
            body = json.loads(event['body'])
            data = body['data']
            
            items = getListOfItems(data)
                
            # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#batch-writing
            with table.batch_writer() as writer:
                for item in items:
                    writer.put_item(Item=item)
            print(items)
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': items
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
            
    elif path == '/url-03' and httpMethod == 'POST':
        try:
            body = json.loads(event['body'])
            data = body['data']
            
            items = getListOfItems(data)
                
            # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#batch-writing
            with table.batch_writer() as writer:
                for item in items:
                    writer.put_item(Item=item)
            print(items)
            
            return formatJSONResponse({
                'statusCode': 200,
                'body': items
            })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
            
            
def getListOfItems(data):
    items = []
    
    for record in data:
        arg = record['arg']
        p = record['path']
        
        # Creating timestamp in number type for dynamo
        # Why use timestamps as numbers in dynamo: https://dynobase.dev/dynamodb-timestamp/
        # Conversion: https://stackoverflow.com/a/7588609
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        timestamp = int(timestamp)
        
        items.append({
            'id': generateAlphanumericID(8),
            'arg': arg,
            'path': p,
            'timestamp': timestamp,
            'type': 'record'
        })
        time.sleep(2)
        
    return items
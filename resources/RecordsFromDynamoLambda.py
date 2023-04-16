import os
import boto3
from boto3.dynamodb.types import TypeDeserializer

def lambda_handler(event, context):
    client = boto3.client('dynamodb')
    
    tableName = os.environ['tableName']
    indexName = os.environ['indexName']
    
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/query.html
    response = client.query(
        TableName=tableName,
        IndexName=indexName,
        # KeyConditionExpression is required so, added additional column type as partition key in GSI to match all records
        KeyConditionExpression='#t = :typeVal',
        ExpressionAttributeValues={
            ':typeVal': {
                'S': 'record'
            }
        },
        ExpressionAttributeNames={
            '#t': 'type',
            '#p': 'path'
        },
        Select='SPECIFIC_ATTRIBUTES',
        ProjectionExpression='id,arg,#p',               # Returning id, arg and path only
        ScanIndexForward=False,                         # Sorts data in descending order
        Limit=10,                                       # Takes 10 records only
    )
    
    data = response['Items']
    
    # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Programming.LowLevelAPI.html
    # Deserializing data: https://stackoverflow.com/a/46738251
    deserializer = TypeDeserializer()
    deserialized_data = []
    
    for record in data:
        d = { k: deserializer.deserialize(v) for k,v  in record.items() }
        deserialized_data.append(d)
        
    return deserialized_data
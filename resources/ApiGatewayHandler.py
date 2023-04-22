import json


def formatJSONResponse(data):
    statusCode = data['statusCode']
    body = data['body'] or None
    
    return {
        'statusCode': statusCode,
        'body': json.dumps(body)
    }
import os
import json
import constants

from ApiGatewayHandler import formatJSONResponse
from CloudWatch import AWSCloudWatch

cw_obj = AWSCloudWatch()

def lambda_handler(event, context):
    # https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html
    path = event['path']
    httpMethod = event['httpMethod']
    
    print(f'Path: {path} ------- httpMethod: {httpMethod}')
    
    if path == '/demo' and httpMethod == 'POST':
        try:
            body = json.loads(event['body'])
            args = body['args']
            
            print(f'args: {args}')
            
            dimensions = [
                {
                    'Name': 'DP01_ARGS',
                    'Value': 'DP01_ARGS_METRIC'
                }
            ]
            cw_obj.cw_put_metric_data(constants.DP01_ARG_METRIC, constants.NAMESPACE, dimensions, args)
            
            if args <= 10:
                return formatJSONResponse({
                    'statusCode': 200,
                    'body': args
                })
            else:
                return formatJSONResponse({
                    'statusCode': 200,
                    'body': {
                        'args': args,
                        'message': 'Alarm is raised'
                    }
                })
        except Exception as e:
            print(e)
            return formatJSONResponse({
                'statusCode': 501,
            })
import os
import json
import boto3

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    log_client = boto3.client('logs')

    admins_topic_arn = os.environ['AdminsSnsTopicArn']
    clients_topic_arn = os.environ['ClientsSnsTopicArn']
    
    log_group = '/aws/lambda/AbdulRaufDesign7Stack-UFLambda1F5A7909-36OHHCHzxDYV'
    log_stream = '2022/12/16/[$LATEST]ac5ad0eb2929424ab04d6e5240a6086e'
    
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs/client/filter_log_events.html
    # Filtering events for admins
    admin_filtered_events = log_client.filter_log_events(
        logGroupName=log_group,
        logStreamNames=[
            log_stream
        ],
        filterPattern='?REPORT',
    )
    admin_filtered_logs = admin_filtered_events['events']
    
    # Filtering events for clients
    client_filtered_events = log_client.filter_log_events(
        logGroupName=log_group,
        logStreamNames=[
            log_stream
        ],
        filterPattern='?START ?END',
    )
    client_filtered_logs = client_filtered_events['events']
        
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/publish.html
    # Sending email to admins
    admin_response = client.publish(
        TopicArn=admins_topic_arn,
        Message=json.dumps(admin_filtered_logs),
        Subject='Lambda cloudwatch logs for admins',
    )
    
    # Sending email to clients
    client_response = client.publish(
        TopicArn=clients_topic_arn,
        Message=json.dumps(client_filtered_logs),
        Subject='Lambda cloudwatch logs for clients',
    )
    
    combined_logs = {
        'Admins': admin_filtered_logs,
        'Clients': client_filtered_logs
    }
    
    return combined_logs
import boto3

client = boto3.client('sns')

def sendEmail(recipient, subject, message):
    # Send email using SNS: https://towardsdatascience.com/working-with-amazon-sns-with-boto3-7acb1347622d
    
    # Create a topic
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/create_topic.html
    response = client.create_topic(
        Name='DP05S3FileContentsWordsCountTopic',
    )
    topicArn = response['TopicArn']
    
    # Subscribing to an SNS topic
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/subscribe.html
    response = client.subscribe(
        TopicArn=topicArn,
        Protocol='email',
        Endpoint=recipient,
        ReturnSubscriptionArn=True
    )
    subscriptionArn = response['SubscriptionArn']
    
    # Sending a SMS to SNS topic
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/publish.html
    response = client.publish(
        TopicArn=topicArn,
        Message=message,
        Subject=subject,
    )
    messageId = response['MessageId']
    
    return messageId
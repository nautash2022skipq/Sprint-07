from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
    aws_iam as iam_,
    aws_apigateway as api_gw_,
    aws_sns_subscriptions as subscriptions_,
    aws_sns as sns_,
    aws_s3 as s3_,
    aws_s3_notifications as s3n_,
    Stack,
    RemovalPolicy,
)
from constructs import Construct

class NautashAhmadStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        role = self.create_lambda_role()
        
        gateway_lambda = self.create_lambda("DP07PresignedUrlLambda", "./resources", "S3PresignUrlLambda.lambda_handler", 
            role, 2
        )
        
        # Removal policy to automatically delete stateless and stateful resources
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk/RemovalPolicy.html#aws_cdk.RemovalPolicy
        gateway_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # Creating SNS topic and subscription
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_sns/Topic.html
        topic = sns_.Topic(self, "DP07S3FileUploadTopic")
        
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_sns_subscriptions/EmailSubscription.html
        topic.add_subscription(subscriptions_.EmailSubscription('nautash.ahmad.skipq@gmail.com'))
        
        # Importing an existing S3 bucket
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3/README.html#importing-existing-buckets
        bucket = s3_.Bucket.from_bucket_attributes(self, 'DP07ImportedBucket',
            bucket_arn='arn:aws:s3:::nautashahmaddp07fileuploadbucket'
        )
        bucket_name = bucket.bucket_name
        
        # Creating a notofication event on S3 bucket
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3_notifications/SnsDestination.html
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_s3/EventType.html
        bucket.add_event_notification(s3_.EventType.OBJECT_CREATED, s3n_.SnsDestination(topic))
        
        # Creating API Gateway
        gw = self.create_rest_api_gateway('DP07ApiGateway')
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/LambdaIntegration.html
        handler = api_gw_.LambdaIntegration(gateway_lambda)
        
        resource_name = 'upload'
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Method.html
        # Authorization type: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/AuthorizationType.html
        # Integration: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Integration.html#aws_cdk.aws_apigateway.Integration
        gw_resource = gw.root.add_resource(resource_name)
        gw_resource.add_method('GET', handler, authorization_type=api_gw_.AuthorizationType.NONE, api_key_required=False)
        
        # Adding environment variable to lambda function
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.add_environment
        gateway_lambda.add_environment('s3bucketName', bucket_name)
        
    # Create Lambda construct
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Function.html
    def create_lambda(self, id, assest_path, handler, role, timeout_min):
        return lambda_.Function(self, 
            id=id,
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler=handler,
            code=lambda_.Code.from_asset(assest_path),
            role=role,
            timeout=Duration.minutes(timeout_min)
        )
        
        
    # Create IAM Role for Lambda
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/Role.html
    def create_lambda_role(self):
        return iam_.Role(self, "DP07UploadFileToS3Role",
            assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
            
            # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/ManagedPolicy.html#aws_cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess")
            ]
        )
        
        
    # Create REST API Gateway
    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/RestApi.html
    def create_rest_api_gateway(self, id):
        return api_gw_.RestApi(self, 
            id=id,
            endpoint_types=[api_gw_.EndpointType.REGIONAL]
        )
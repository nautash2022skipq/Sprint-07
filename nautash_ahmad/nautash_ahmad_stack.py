from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
    aws_iam as iam_,
    aws_apigateway as api_gw_,
    Stack,
    RemovalPolicy,
)
from constructs import Construct

class NautashAhmadStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        role = self.create_lambda_role()
        
        fn = self.create_lambda("DP07PresignedUrlLambda", "./resources", "S3PresignUrlLambda.lambda_handler", 
            role, 2
        )
        
        # Removal policy to automatically delete stateless and stateful resources
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk/RemovalPolicy.html#aws_cdk.RemovalPolicy
        fn.apply_removal_policy(RemovalPolicy.DESTROY)
            
        '''
            Creating lambda handler and API Gateway for REST API endpoint for getting S3 presigned url
        '''
        # Creating lambda for GW dynamo handler
        gw_dynamo_lambda = self.create_lambda("DP07ApiGatewayLambda", "./resources", "EmailNotificationLambda.lambda_handler", 
            role, 5
        )
        
        # Adding environment variable to Lambda
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.add_environment
        gw_dynamo_lambda.add_environment('tableName', gw_dynamo_table.table_name)
        
        # Creating API Gateway
        gw = self.create_rest_api_gateway('DP07ApiGateway')
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/LambdaIntegration.html
        handler = api_gw_.LambdaIntegration(gw_dynamo_lambda)
        
        resource_name = 'upload'
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Method.html
        # Authorization type: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/AuthorizationType.html
        # Integration: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Integration.html#aws_cdk.aws_apigateway.Integration
        gw_resource = gw.root.add_resource(resource_name)
        gw_resource.add_method('GET', handler, authorization_type=api_gw_.AuthorizationType.NONE, api_key_required=False)
        
        # Constructing REST API Gateway URL
        # https://docs.aws.amazon.com/apigateway/latest/developerguide/create-api-resources-methods.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/RestApiAttributes.html#aws_cdk.aws_apigateway.RestApiAttributes.rest_api_id
        api_gateway_url = 'https://' + gw.rest_api_id + '.execute-api.' + self.region + '.amazonaws.com/prod/' + resource_name
        
        # Adding environment variable to lambda function
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.add_environment
        fn.add_environment('apiGatewayUrl', api_gateway_url)
        
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
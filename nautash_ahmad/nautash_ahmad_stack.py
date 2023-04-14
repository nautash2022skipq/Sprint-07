from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
    aws_iam as iam_,
    aws_dynamodb as dynamo_,
    aws_apigateway as api_gw_,
    Stack,
    RemovalPolicy,
)
from constructs import Construct

class NautashAhmadStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        role = self.create_lambda_role()
        
        fn = self.create_lambda("ApiGatewayWebHealthLambda", "./resources", "WebHealthAppLambda.lambda_handler", 
            role, 2
        )
        
        # Removal policy to automatically delete stateless and stateful resources
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk/RemovalPolicy.html#aws_cdk.RemovalPolicy
        fn.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # Creating lambda for dynamo handler
        dynamo_lambda = self.create_lambda("ApiGatewayWebHealthDynamoLambda", "./resources", "WebHealthDynamoLambda.lambda_handler", 
            role, 2
        )
        
        # Creating DynamoDB table
        dynamo_table = self.create_dynamodb_table('ApiGatewayWebHealthDynamoTable', 'id', 'timestamp')
        dynamo_table.grant_full_access(dynamo_lambda)
        
        # Adding environment variable to Lambda
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.add_environment
        dynamo_lambda.add_environment('tableName', dynamo_table.table_name)
            
        '''
            Creating DynamoDB table, DynamoDB lambda handler and API Gateway for REST API endpoints for CRUD Operations
        '''
        # Creating lambda for GW dynamo handler
        gw_dynamo_lambda = self.create_lambda("ApiGatewayCrudDynamoLambda", "./resources", "ApiGatewayCrudDynamoLambda.lambda_handler", 
            role, 5
        )
        
        # Creating DynamoDB table for API Gateway CRUD Operations
        gw_dynamo_table = self.create_dynamodb_table('ApiGatewayCRUDTable', 'id')
        gw_dynamo_table.grant_full_access(gw_dynamo_lambda)
        
        # Adding environment variable to Lambda
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.add_environment
        gw_dynamo_lambda.add_environment('tableName', gw_dynamo_table.table_name)
        
        # Creating API Gateway
        gw = self.create_rest_api_gateway('TestRestApiGateway')
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/LambdaIntegration.html
        handler = api_gw_.LambdaIntegration(gw_dynamo_lambda)
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Method.html
        # Authorization type: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/AuthorizationType.html
        # Integration: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Integration.html#aws_cdk.aws_apigateway.Integration
        resource_name = 'url-01'
        gw_resource = gw.root.add_resource(resource_name)
        gw_resource.add_method('POST', handler, authorization_type=api_gw_.AuthorizationType.NONE, api_key_required=False)
        
        resource_name = 'url-02'
        gw_resource = gw.root.add_resource(resource_name)
        gw_resource.add_method('POST', handler, authorization_type=api_gw_.AuthorizationType.NONE, api_key_required=False)
        
        resource_name = 'url-03'
        gw_resource = gw.root.add_resource(resource_name)
        gw_resource.add_method('POST', handler, authorization_type=api_gw_.AuthorizationType.NONE, api_key_required=False)
        
        
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
        return iam_.Role(self, "ApiGatewayWebHealthAppLambdaRole",
            assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
            
            # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/ManagedPolicy.html#aws_cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
            ]
        )
        
        
    # Create AWS DynamoDB table
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_dynamodb/Table.html
    def create_dynamodb_table(self, id, partition_key, sort_key=None):
        attr = {
            'id': id,
            'partition_key': dynamo_.Attribute(name=partition_key, type=dynamo_.AttributeType.STRING),
            'billing_mode': dynamo_.BillingMode.PAY_PER_REQUEST,
            'removal_policy': RemovalPolicy.DESTROY,
        }
        
        # Optionalyy adding sort key to DynamoDB
        if sort_key:
            attr.update({'sort_key': dynamo_.Attribute(name=sort_key, type=dynamo_.AttributeType.STRING)})
        
        # Unpacking dictionary items
        return dynamo_.Table(self,
            **attr
        )
        
        
    # Create REST API Gateway
    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/RestApi.html
    def create_rest_api_gateway(self, id):
        return api_gw_.RestApi(self, 
            id=id,
            endpoint_types=[api_gw_.EndpointType.REGIONAL]
        )
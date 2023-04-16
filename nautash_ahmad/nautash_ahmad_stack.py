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
        
        # Creating lambda handler to get ten latest records from dynamo
        dynamo_get_lambda = self.create_lambda("DP02DifferentUrlsDynamoGetLambda", "./resources", "RecordsFromDynamoLambda.lambda_handler", 
            role, 2
        )
        
        # Removal policy to automatically delete stateless and stateful resources
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk/RemovalPolicy.html#aws_cdk.RemovalPolicy
        dynamo_get_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
            
        '''
            Creating DynamoDB table, lambda handler and API Gateway for REST API endpoints for CRUD Operations
        '''
        # Creating lambda handler for GW to add data to dynamo by POST requests
        gw_dynamo_lambda = self.create_lambda("DP02DifferentUrlsGWLambda", "./resources", "ApiGatewayCrudDynamoLambda.lambda_handler", 
            role, 5
        )
        gw_dynamo_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        
        partition_key = 'id'
        sort_key = 'timestamp'
        index_name = 'DP02TimestampGSI'
        
        # Creating DynamoDB table for API Gateway POST Operations
        gw_dynamo_table = self.create_dynamodb_table('DP02DifferentApiUrlsDynamoTable', partition_key, sort_key)
        gw_dynamo_table.grant_full_access(gw_dynamo_lambda)
        
        # Adding GSI on dynamo table for filtering and pagination
        # Creating a column 'type' as partition key to match all records as partition key is requird in KeyConditionExpression
        # Docs: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html#GSI.ThroughputConsiderations
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_dynamodb/Table.html#aws_cdk.aws_dynamodb.Table.add_global_secondary_index
        gw_dynamo_table.add_global_secondary_index(read_capacity=10, write_capacity=10, index_name=index_name,
            partition_key=dynamo_.Attribute(name='type', type=dynamo_.AttributeType.STRING),
            sort_key=dynamo_.Attribute(name=sort_key, type=dynamo_.AttributeType.NUMBER)
        )
        
        # Adding environment variable to Lambda
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.add_environment
        gw_dynamo_lambda.add_environment('tableName', gw_dynamo_table.table_name)
        dynamo_get_lambda.add_environment('tableName', gw_dynamo_table.table_name)
        dynamo_get_lambda.add_environment('indexName', index_name)
        
        # Creating API Gateway
        gw = self.create_rest_api_gateway('DP02DifferentUrlsApiGateway')
        
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
        return iam_.Role(self, "DP02DifferentUrlsRole",
            assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
            
            # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/ManagedPolicy.html#aws_cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
            ]
        )
        
        
    # Create AWS DynamoDB table
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_dynamodb/Table.html
    def create_dynamodb_table(self, id, partition_key, sort_key=None):
        attr = {
            'id': id,
            'partition_key': dynamo_.Attribute(name=partition_key, type=dynamo_.AttributeType.STRING),
            'removal_policy': RemovalPolicy.DESTROY,
        }
        
        # Optionally adding sort key to DynamoDB
        if sort_key:
            attr.update({'sort_key': dynamo_.Attribute(name=sort_key, type=dynamo_.AttributeType.NUMBER)})
        
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
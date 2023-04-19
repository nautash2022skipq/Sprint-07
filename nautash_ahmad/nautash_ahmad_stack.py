from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
    aws_iam as iam_,
    Stack,
    RemovalPolicy,
)
from constructs import Construct

class NautashAhmadStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        role = self.create_lambda_role()
        
        fn = self.create_lambda("DP05S3FilesReadLambda", "./resources", "FileReaderLambda.lambda_handler", 
            role, 10
        )
        
        # Removal policy to automatically delete stateless and stateful resources
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk/RemovalPolicy.html#aws_cdk.RemovalPolicy
        fn.apply_removal_policy(RemovalPolicy.DESTROY)
        
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
        return iam_.Role(self, "DP05S3FilesReadRole",
            assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
            
            # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/ManagedPolicy.html#aws_cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess")
            ]
        )
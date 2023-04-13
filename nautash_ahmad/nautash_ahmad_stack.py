from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
    aws_iam as iam_,
    aws_cloudwatch as cw_,
    aws_sns as sns_,
    aws_sns_subscriptions as subscriptions_,
    aws_cloudwatch_actions as cw_actions_,
    aws_apigateway as api_gw_,
    Stack,
    RemovalPolicy,
)
from constructs import Construct
from resources import constants

class NautashAhmadStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        role = self.create_lambda_role()
        
        # Creating lambda for GW handler
        gw_lambda = self.create_lambda("DP01ArgAlarmLambda", "./resources", "ApiGatewayLambda.lambda_handler", 
            role, 5
        )
        
        gw_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # Creating SNS topic and subscription
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_sns/Topic.html
        topic = sns_.Topic(self, "ArgMetricAlarmTopic")
        
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_sns_subscriptions/EmailSubscription.html
        topic.add_subscription(subscriptions_.EmailSubscription('nautash.ahmad.skipq@gmail.com'))
        
        '''
            Creating metric for <arg> varaible received in body
            Alarm will be created for this metric
        '''
        dimensions = {'DP01_ARGS': 'DP01_ARGS_METRIC'}
        arg_metric = self.create_cw_metric(constants.DP01_ARG_METRIC, constants.NAMESPACE, dimensions)
        arg_metric_alarm = self.create_cw_alarm(f'arg_metric_errors', 10, cw_.ComparisonOperator.GREATER_THAN_THRESHOLD, constants.MINS, arg_metric)
    
        # Connecting CloudWatch alarms with SNS topic to send notifications when alaram is triggered
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudwatch_actions/SnsAction.html
        arg_metric_alarm.add_alarm_action(cw_actions_.SnsAction(topic))
            
        '''
            Creating API Gateway for REST API endpoint for POST method only
        '''
        
        # Creating API Gateway
        gw = self.create_rest_api_gateway('DP01ArgApiGateway')
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/LambdaIntegration.html
        handler = api_gw_.LambdaIntegration(gw_lambda)
        
        resource_name = 'demo'
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Method.html
        # Authorization type: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/AuthorizationType.html
        # Integration: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Integration.html#aws_cdk.aws_apigateway.Integration
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
        return iam_.Role(self, "DP01ArgAlarmRole",
            assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
            
            # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/ManagedPolicy.html#aws_cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess")
            ]
        )
        
        
    # Create CloudWatch alarm
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudwatch/Alarm.html
    def create_cw_alarm(self, id, threshold, comparison_operator, mins, metric):
        return cw_.Alarm(self, 
            id=id,
            threshold=threshold,
            comparison_operator=comparison_operator,
            evaluation_periods=mins,
            metric=metric
        )
        
        
    # Create CloudWatch metric
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudwatch/Metric.html
    def create_cw_metric(self, metric_name, namespace, dimensions):
        return cw_.Metric(
            metric_name=metric_name,
            namespace=namespace,
            dimensions_map=dimensions
        )
        
        
    # Create REST API Gateway
    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/RestApi.html
    def create_rest_api_gateway(self, id):
        return api_gw_.RestApi(self, 
            id=id,
            endpoint_types=[api_gw_.EndpointType.REGIONAL]
        )
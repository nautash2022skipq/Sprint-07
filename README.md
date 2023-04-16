
# Design Problem 02

## Problem Statement - Design & Develop

Consider that you are getting events in the format `[{“event1”:{“attr1”: value }}]` from different APIs.
1.  How will you parse the event to get the value?
2.  How will you return 10 latest events when required?

## Architecture Design
![Web Health App Architecture Diagram](public/images/DesignProblem02.jpg)

<br>

* [Seting up the Project](#seting-up-the-project)

* [AWS services used in this project](#aws-services-used-in-this-project)

* [API Gateway Endpoint Method(s)](#api-gateway-endpoint-methods)

* [Useful commands](#useful-commands)

<br>


## Seting up the Project

To start with the project:

Create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

Finally, to deploy your stack to AWS.

```
$ cdk deploy
```

And if you have multiple AWS account configured then you need to pass the `--profile` parameter.

```
$ cdk deploy <PipelineStackName> --profile username
```

## AWS services used in this project

This project requires follwing services to run

- AWS Lambda
- IAM Role
- DynamoDB
- CloudFormation
- API Gateway

## API Gateway Endpoint Methods
In this project, we have created **REST API with AWS API Gateway** backed by **Lambda**.

API Gateway will generate URL which will be used to send HTTP requests at. Following method can be used to send request to this URL generated by API Gateway:

* **POST**

User can send the **POST** request to any of these URLs
>- https://some-url/prod/url-01
>- https://some-url/prod/url-02
>- https://some-url/prod/url-03

Data needs to be in the body in a `JSON` format

```
{
    "args": 10
}
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
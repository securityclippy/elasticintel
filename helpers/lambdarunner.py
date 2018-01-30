import boto3
import json
import os

class LambdaRunner(object):
    def __init__(self, region):
        self.region = region
        self.lambda_client = boto3.client('lambda',
                                          #aws_access_key=os.environ['AWS_ACCESS_KEY_ID'],
                                          #aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                                          region_name=region)

    def run_lambda(self, lambda_func, event):
        lambda_response = self.lambda_client.invoke(FunctionName=lambda_func,
                                                    Payload=json.dumps(event), InvocationType='RequestResponse')

        response = lambda_response['Payload'].read()
        jresponse = json.loads(response.decode())
        return jresponse
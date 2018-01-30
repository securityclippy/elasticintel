import logging
import os

import boto3

import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth

logging.basicConfig()
LOGGER = logging.getLogger("ElasticIntelManager")
LOGGER.setLevel(logging.INFO)

class ElasticIntelManager(object):
    def __init__(self, host, index):
        self.host = host
        self.index = index
        self.uri = "https://{}".format(host)
        self.headers = {"Content-Type": "application/json"}
        self.session = requests.session()
        self.session.headers = self.headers
        self.boto_session = boto3.Session()
        self.aws_auth = self.boto_session.get_credentials()
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            print("flerp")
            self.auth = AWSRequestsAuth(aws_access_key=os.environ['AWS_ACCESS_KEY_ID'],
                                   aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                                   aws_token=os.environ['AWS_SESSION_TOKEN'],
                                   aws_host=host,
                                   aws_region='us-east-1',
                                   aws_service='es')

    def create_index(self, index_name=None):
        if index_name:
            response = self.session.post("{}/{}".format(self.uri, index_name), auth=self.auth)
        else:
            response = self.session.post("{}/{}".format(self.uri, self.index), auth=self.auth)
        LOGGER.debug(response.text)

    def add(self, intel):
        data = intel.to_json()
        response = self.session.post("{}/{}/intel/".format(self.uri, self.index), data=data, auth=self.auth, timeout=10)
        LOGGER.debug(response.text)
        return response.status_code

    def bulk_add(self, intel_list):
        data = ""
        for i in intel_list:
            if type(i) != str:
                data += '{"index": {}}'
                data += "\n"
                data += i.to_json()
                data += "\n"
        LOGGER.debug(len(data))
        response = self.session.post("{}/{}/intel/_bulk".format(self.uri, self.index), data=data, auth=self.auth)
        LOGGER.debug(response.text)


#!/usr/bin/env python3

from iocsearch import IOCSearch
import os
import json

#/iocs/search/ipaddress
#/iocs/search/domain
#/iocs/search/url
#/iocs/search/string

class IOCRequest(object):
    def __init__(self, event):
        self.type = event['type']
        self.searchstring = event['searchstring']

def return_results(body):
    return_dict = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
    return return_dict



def handler(event, context):
    es_host = os.environ['ES_HOST']
    print("ES: {}".format(es_host))
    print(event)
    params = event['pathParameters']
    r = IOCRequest(params)
    print("request indicator type: {}".format(r.type))
    iocs = IOCSearch(es_instance_host=es_host, is_lambda=True)
    if event['resource'].split("/")[-1] == "summary":

        if r.type == "ipaddress":
            ans = iocs.ip_details(r.searchstring)
            return return_results(ans)
        elif r.type == "domain":
            return iocs.domain_details(r.searchstring)
        elif r.type == "url":
            return iocs.stringsearch(r.searchstring)
        elif r.type == "string":
            return iocs.stringsearch(r.searchstring)
    return return_results({"message": "error, not found"})

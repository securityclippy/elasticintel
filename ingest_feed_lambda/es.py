#!/usr/bin/env python3

import requests
import os
import json
import timeit
from time import sleep
from aws_requests_auth.aws_auth import AWSRequestsAuth
try:
    from ingest_feed_lambda.ioc_feed_parser import IOCFeedParser
except:
    from ioc_feed_parser import IOCFeedParser


class ES(object):
    def __init__(self, es_host, region='us-east-1', is_lambda=True,  index='iocs'):
        AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
        AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
        if is_lambda:
            aws_token = os.environ["AWS_SESSION_TOKEN"]
            self.auth = AWSRequestsAuth(aws_access_key=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                aws_token=aws_token,
                                aws_host=es_host,
                                aws_region=region,
                                aws_service='es')
        else:
            self.auth = AWSRequestsAuth(aws_access_key=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        aws_host=es_host,
                                        aws_region=region,
                                        aws_service='es')
        self.session = requests.session()
        self.session.auth = self.auth
        self.es_host = es_host

    def bulk_item_upsert(self, items):
        index = "iocs"
        data = ""
        for item in items:
            data += json.dumps({"index": {"_index": index, "_type": "ioc"}})
            data += "\n"
            data += item
            data += "\n"
        self.session.headers.update({"Content-Type": "application/json"})
        print("Session Headers: {}".format(self.session.headers))
        r = self.session.post("https://{host}/_bulk".format(host=self.es_host), data=data)
        if r.status_code != 200:
            print(r.text)
        return

    def chunk_items(self,  items, chunk_size=1000):
        for i in range(0, len(items), chunk_size):
            yield items[i:i+chunk_size]

    def bulk_es_index_dataframe(self, es_index, df):
        start = timeit.default_timer()
        try:
            items = df.to_json(orient='records', lines=True).split("\n")
        except Exception as e:
            print(e)
            print(df)
        print("Uploading {} items...".format(len(items)))
        chunks = self.chunk_items(items=items)
        for i in chunks:
            self.bulk_item_upsert(i)
        elapsed = timeit.default_timer() - start
        print("Upload took: {}".format(elapsed))
        return

    def query_ip(self, ipaddress):
        data = {
          "size": 500,
          "query": {
            "bool": {
              "must": [
                {
                  "term": {
                    "ipaddress.keyword": {
                      "value": ipaddress
                    }
                  }
                }
              ]
            }
          }
        }
        r = self.session.get("https://{host}/{index}/_search".format(host=self.es_host, index="new_threat_index"), data=json.dumps(data))
        #if r.status_code == 200:
        return r.text

    def query(self, query):
        '''
        returns dict of query response
        :param query:
        :return:
        '''
        return json.loads(self.session.get("https://{host}/{index}/_search".format(host=self.es_host, index="new_threat_index"), data=json.dumps(query)).text)

    def query_ip_summary(self, answer_text):
        ans = json.loads(answer_text)
        count = ans['hits']['total']
        source_counts = {}
        for hit in ans['hits']['hits']:
            sauce = hit['_source']
            if sauce['source'] in source_counts.keys():
                source_counts[sauce['source']] += 1
            else:
                source_counts[sauce['source']] = 1

        print(count, source_counts)


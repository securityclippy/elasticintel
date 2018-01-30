import requests
import os
import json
import timeit
from time import sleep
from aws_requests_auth.aws_auth import AWSRequestsAuth
from multiprocessing.pool import ThreadPool

class ES(object):
    def __init__(self, es_host, region='us-east-1', is_lambda=True):
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
        self.session.headers.update({"Content-Type": "application/json"})
        self.es_host = es_host

    def query(self, query):
        '''
        returns dict of query response
        :param query:
        :return:
        '''
        return json.loads(
            self.session.get("https://{host}/{index}/_search".format(host=self.es_host, index="iocs"),
                             data=json.dumps(query)).text)


class IOCSearch(object):
    def __init__(self, es_instance_host, is_lambda=False):
        self.es = ES(es_host=es_instance_host, is_lambda=is_lambda)

    def ip_summary(self, ipaddress):
        query = {
              "size": 0,
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
              },
              "aggs": {
                "sources": {
              "terms": {
                "field": "source.keyword"
              }
            }
          }
        }
        return self.es.query(query=query)

    def ip_details(self, ipaddress):
        query = {
            "size": 10,
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "ipaddress.keyword": {
                                    "value": "{}".format(ipaddress)
                                }
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "sources": {
                    "terms": {
                        "field": "source.keyword"
                    }
                }
            }
        }
        print(query)
        return self.es.query(query=query)

    def stringsearch(self, string):
        query = {
            "query": {
                "query_string": {
                    "query": string
                }
            }
        }
        ans = self.es.query(query)
        return ans

    def stringsearch_summary(self, string):
        query = {
            "size": 0,
            "query": {
                "query_string": {
                    "query": string
                }
            },
            "aggs": {
                "sources": {
                    "terms": {
                        "field": "source.keyword"
                    }
                }
            }
        }
        ans = self.es.query(query)
        return ans

    def domain_details(self, domain):
        query = {
              "size": 500,
              "query": {
                "bool": {
                  "must": [
                    {
                      "wildcard": {
                        "domain.keyword": {
                          "value": "*{}*".format(domain)
                        }
                      }
                    }
                  ]
                }
              },
              "aggs": {
                "sources": {
                  "terms": {
                    "field": "source.keyword"
                  }
                }
              }
            }
        print(query)
        return self.es.query(query=query)

    def domain_summary(self, domain):
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {
                            "wildcard": {
                                "domain.keyword": {
                                    "value": "{}".format(domain)
                                }
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "sources": {
                    "terms": {
                        "field": "source.keyword"
                    }
                }
            }
        }
        print(query)
        return self.es.query(query=query)

    def proxy_details(self, proxy):
        query = {
            "size": 500,
            "query": {
                "bool": {
                    "must": [
                        {
                            "wildcard": {
                                "proxy.keyword": {
                                    "value": "*{}*".format(proxy)
                                }
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "sources": {
                    "terms": {
                        "field": "source.keyword"
                    }
                }
            }
        }
        return self.es.query(query=query)

    def proxy_summary(self, proxy):
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {
                            "wildcard": {
                                "proxy.keyword": {
                                    "value": "*{}*".format(proxy)
                                }
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "sources": {
                    "terms": {
                        "field": "source.keyword"
                    }
                }
            }
        }
        return self.es.query(query=query)


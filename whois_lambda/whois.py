from ipwhois.ipwhois import IPWhois
import ipwhois
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import timeit
import json
from time import sleep
from datetime import datetime, timedelta
import os
import multiprocessing
import threading
import time
import random


class LambdaWhois(object):
    def __init__(self, thread_timeout=None, chunk=None, size=None, is_lambda=True, verbose_logging=False):
        '''
        an init, because  reasons
        '''
        self.verbose_logging = verbose_logging
        if thread_timeout is None:
            thread_timeout = 10
        self.process_timeout = thread_timeout
        region = 'us-east-1' # e.g. us-east-1
        if chunk is None:
            chunk = 25
        self.chunk = chunk
        if size is None:
            size = 600
        self.size = size
        self.procs = []
        #self.process_timeout = 6
        self.es_host = os.environ['ES_HOST']
        AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
        AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
        if is_lambda:
            aws_token = os.environ["AWS_SESSION_TOKEN"]
            self.auth = AWSRequestsAuth(aws_access_key=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        aws_token=aws_token,
                                        aws_host=self.es_host,
                                        aws_region=region,
                                        aws_service='es')
        else:
            self.auth = AWSRequestsAuth(aws_access_key=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        aws_host=self.es_host,
                                        aws_region=region,
                                        aws_service='es')
        self.session = requests.session()
        self.session.auth = self.auth
        #ES 6.0+ requires explicit Content-Type headers
        self.session.headers.update({"Content-Type": "application/json"})
        self.whois_answers = []

    def get_from_range(self):
        region_map = {
            "us-east-1": 0,
            "us-east-2": 700,
            "us-west-1": 1400,
            "us-west-2": 2100,
            "ca-central-1": 2800,
            "eu-west-1": 3500,
            "eu-west-2": 4200,
            "eu-central-1": 4900,
            "ap-northeast-1": 5600,
            "ap-northeast-2": 6300,
            "ap-southeast-1": 7000,
            "ap-southeast-2": 7700,
            "ap-south-1": 8500,
            "sa-east-1": 9200
        }
        return region_map[os.environ['AWS_REGION']]

    def get_items_to_update(self):
        with open("get_null_whois.json") as infile:
            query = json.load(infile)
        query["from"] = self.get_from_range()
        query["size"] = self.size
        '''query = {
                  "from": self.get_from_range(),
                  "size": self.size,
                  "query": {
                    "bool": {
                      "must": [{
                        "term": {
                          "indicator_type.keyword": {
                            "value": "ipaddress"
                          }
                        }
                      },
                        {
                          "range": {
                            "whois_last_updated": {
                              "lte": "now-2d"
                            }
                          }
                        }
                      ]
                    }
                  },
            "sort": [
                    {
                      "indexed_at": {
                        "order": "desc"
                      }
                    }
                  ]
                }'''
        r = self.session.get("https://{host}/{index}/_search".format(host=self.es_host, index="iocs"),
                        data=json.dumps(query))
        if not r.status_code == 200:
            print("Status code: ".format(r.status_code))
            print(r.text)
            return
        print("total hits:")
        print(json.loads(r.text)['hits']['total'])
        return json.loads(r.text)['hits']['hits']

    def create_whois_summary(self, whois_info):
        try:
            cidr = whois_info['network']['cidr']
            country = whois_info['network']['country']
            name = whois_info['network']['name']
            k = list(whois_info['objects'].keys())[0]
            address = whois_info['objects'][k]['contact']['address'][0]['value']
            email = whois_info['objects'][k]['contact']['email'][0]['value']
            whois_summary = "{}, {}, {}, {}".format(name, country, address, email).replace("\n", ", ").replace("\\n", ", ")
        except Exception as e:
            return
        return whois_summary


    #@timeout(10, "whois lookup timed out")
    def get_ip_whois(self, item, conn):
        #set our default values, assuming we ever get an answer
        whois_last_updated = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        item['_source']['whois_last_updated'] = whois_last_updated
        item['_source']['whois'] = None
        ipaddr = item['_source']['ipaddress']
        lookup_successful = False
        try:
            ans = IPWhois(ipaddr, timeout=5).lookup_rdap(depth=1, rate_limit_timeout=5)
            if ans:
                lookup_successful = True
                whois_last_updated = (datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")
                item['_source']['whois_last_updated'] = whois_last_updated
                item['_source']['whois'] = json.dumps(ans)
                try:
                    item['_source']['whois_summary'] = self.create_whois_summary(ans)
                except Exception as e:
                    print(e)
                    pass
        except Exception as e:
            pass
        conn.send([item, lookup_successful])
        return


    def lookup_ip(self, item, conn):
        thread_timeout = self.process_timeout
        _start = time.time()
        updated = ""
        ans = ""
        while time.time() - _start <= thread_timeout:
            ipaddr = item['_source']['ipaddress']
            timeout = time.time()
            try:
                if not ans:
                    ans = IPWhois(ipaddr, timeout=5).lookup_rdap(depth=1, rate_limit_timeout=5)
                if ans:
                    #print("breaking out of loop")
                    break
                else:
                    print('hit timeout')
                    #set last updated so that it will appear in search 6 hours from now
                    whois_last_updated = (datetime.now() - timedelta(weeks=2, hours=6)).strftime("%Y-%m-%dT%H:%M:%S")
                    ans = {"error": "whois lookup timedout"}
                    item['_source']['whois_last_updated'] = whois_last_updated
                    item['_source']['whois'] = json.dumps(ans)
                    conn.send(item)
                    return
            except Exception as e:
                up = datetime.now() - timedelta(weeks=2, hours=6)
                whois_last_updated = up.strftime("%Y-%m-%dT%H:%M:%S")
                item['_source']['whois_last_updated'] = whois_last_updated
                if self.verbose_logging:
                    print("Got an exception!: {}".format(e))
                    print(item)
                if type(e) == ipwhois.exceptions.HTTPLookupError:
                    ans = {"error": "404"}
                    item['_source']['whois'] = json.dumps(ans)
                    conn.send(item)
                    return
                elif type(e) == ipwhois.exceptions.IPDefinedError:
                    print("network defined")
                    item['_source']['whois'] = json.dumps(ans)
                    conn.send(item)
                    return
                elif type(e) == ipwhois.HTTPRateLimitError:
                    conn.send(item)
                    return
                else:
                    ans = None
            if ans:
                try:
                    cidr = ans['network']['cidr']
                    country = ans['network']['country']
                    name = ans['network']['name']
                    k = list(ans['objects'].keys())[0]
                    address = ans['objects'][k]['contact']['address'][0]['value']
                    email = ans['objects'][k]['contact']['email'][0]['value']
                    whois_summary = "{}, {}, {}, {}".format(name, country, address, email).replace("\n", ", ").replace("\\n", ", ")
                    up = datetime.now()
                    whois_last_updated = up.strftime("%Y-%m-%dT%H:%M:%S")
                except Exception as e:
                    if self.verbose_logging:
                        print("Got an exception!: {}".format(e))
                    whois_summary = None
                    up = datetime.now()
                    whois_last_updated = up.strftime("%Y-%m-%dT%H:%M:%S")
                    pass
                item['_source']['whois'] = json.dumps(ans)
                item['_source']['whois_last_updated'] = whois_last_updated
                if whois_summary:
                    item['_source']['whois_summary'] = whois_summary
            conn.send(item)
            return
        print("hit thread timeout")
        return

    def update_es_items(self, items):
        update_body = ""
        for item in items:
            update_body += json.dumps({"update": {"_id": item['_id']}})
            update_body += "\n"
            update_body += json.dumps({"doc": {"whois": item['_source']['whois'],
                                               "whois_last_updated": item['_source']['whois_last_updated']}})
            update_body += "\n"
            self.session.headers.update({"Content-Type": "application/json"})
        r = self.session.post("https://{host}/{index}/ioc/_bulk".format(host=self.es_host, index="iocs"),
                         data=update_body)
        return r

    def chunk_upload_set(self, upload_set):
        for i in range(0, len(upload_set),  self.chunk):
            yield upload_set[i:i+self.chunk]

    def lookup_and_upload(self, upload_set):
        '''
        take in a list  of dictionaries,  lookup the whois information for them and upload them to elasticsearch
        :param upload_set:
        :return:
        '''
        successful_whois = 0
        _upload_start = time.time()
        print("starting...")
        random.shuffle(upload_set)
        chunks = self.chunk_upload_set(upload_set)
        to_be_uploaded = []
        for chunk in chunks:
            if chunk and time.time() - _upload_start <= 260:
                not_in_es_subset = chunk
                _start = time.time()
                proc_num= 0
                answers = []
                parent_cons = []
                start = timeit.default_timer()
                for item in not_in_es_subset:
                    if item:
                        parent_conn, child_conn = multiprocessing.Pipe()
                        proc_num += 1
                        t = threading.Thread(target=self.get_ip_whois, args=(item, child_conn, ), name="thread_{}".format(proc_num))
                        parent_cons.append(parent_conn)
                        self.procs.append(t)
                        t.start()
                print("started {} proccesses".format(proc_num))
                while time.time() - _start <= self.process_timeout:
                    if any(p.is_alive() for p in self.procs):
                        time.sleep(.5)
                    else:
                        print('all threads finished!')
                        time.sleep(1)
                        break
                else:
                    print("reached timeout, killing processes, waiting 10 seconds to join all")
                    for p in self.procs:
                        p.join(self.process_timeout)
                try:
                    for p_conn in parent_cons:
                        a = p_conn.recv()
                        item = a[0]
                        success = a[1]
                        answers.append(item)
                        if success:
                            successful_whois += 1
                    print("Total successful lookups so far: {}".format(successful_whois))
                except:
                    print("No answers found yet")
                    pass
                elapsed = timeit.default_timer() - start
                #print("Finished lookup in {} in seconds".format(elapsed))
                if answers:
                    to_be_uploaded += answers
                    #print("total to be uploaded: {}".format(len(to_be_uploaded)))
        result = json.loads(self.update_es_items(to_be_uploaded).text)
        if "errors" in result.keys():
            if result['errors'] == True:
                print(result)
                return
        if "items" in result.keys():
            print("Total updated: {}".format(len(result['items'])))
        print("successful lookups: {}/{}".format(successful_whois, len(to_be_uploaded)))
        return


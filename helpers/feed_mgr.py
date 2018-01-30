from datetime import datetime

import boto3

import requests

try:
    from elastic_intel_manager import ElasticIntelManager
except:
    from helpers.elastic_intel_manager import ElasticIntelManager
try:
    from intelparser import IntelParser
except:
    from helpers.intelparser import IntelParser


class FeedManager(object):
    def __init__(self, event):
        host = event['es_endpoint']
        intel_index = event['intel_index']
        self.elastic_intel = ElasticIntelManager(host=host, index=intel_index)
        self.intel_parser = IntelParser()
        self.event = event

    def feed_timestamp(self):
        return datetime.now().strftime("%Y-%m-%dT%H:%M")

    def get_feed(self, feed_dict):
        '''
        :param feed_dict:
        :return:
        '''
        try:
            response = requests.get(feed_dict['feed_url'])
            if response.status_code == 200:
                print("got response len of {} ".format(len(response.text)))
                #LOGGER.debug("Got statuscode 200 for {}".format(feed))
                feed_name = feed_dict['feed_name']
                feed_type = feed_dict['feed_type']
                #save to s3 here
                #with open(feed_name+"."+feed_type, "w") as wb:
                    #wb.write(response.text)
            return response.text
        except Exception as e:
            #LOGGER.info(e)
            return False

    def save_to_s3(self, feed_data, feed_dict):
        '''
        1. check if folder for feed exists in s3 bucket
        2. create if not exists
        3. save feed copy with today's data + feed name
        save a dated copy of intel to s3
        :param feed_dict:
        :return:
        '''
        s3 = boto3.resource('s3')
        bucket_name = self.event['bucket_name']
        with open("/tmp/feed.txt", "w") as feedfile:
            feedfile.write(feed_data)
        #check if our bucket exists.  Create it if it doesn't
        try:
            s3.Bucket(bucket_name).load()
            bucket = s3.Bucket(bucket_name)
        except:
            print("bucket does not exist.  Creating {}...".format(bucket_name))
            s3.Bucket(bucket_name).create()
            bucket = s3.Bucket(bucket_name)
        feed_name = feed_dict['feed_name']
        #check if the feed folder exits.  Create it if it doesn't
        try:
            bucket.Object(feed_name+"/").load()
        except Exception as e:
            print("feed folder does not exist.  Creating {}".format(feed_dict['feed_name']))
            bucket.Object(feed_name+"/").put()
        bucket.upload_file('/tmp/feed.txt', '{}/{}-{}'.format(feed_name, feed_name, self.feed_timestamp()))

    def parse_feed(self, feed_data, feed_dict):
        '''
        read the data line for line and return valid Intel objects
        :param feed_data:
        :return:
        '''
        intel_objs = IntelParser.parse_feed(feed_data, feed_dict)
        return intel_objs

    def index_feed_data(self, intel_objects_list):
        '''
        send intel objects to elasticsearch
        :param intel_objects_list:
        :return:
        '''
        results = []
        try:
            self.elastic_intel.create_index(index_name=self.event['index_name'])
        except Exception as e:
            print(e)
        for i in intel_objects_list:
            if self.elastic_intel.add(i) == 201:
                results.append(200)
            else:
                results.append(500)
        return results
        #elastic_intel.bulk_add(intel_objects_list)



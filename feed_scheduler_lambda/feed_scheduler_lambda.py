#!/usr/bin/env python3

import json
import os
import shutil
from time import sleep
from datetime import datetime

import boto3



class FeedScheduler(object):
    '''
    FeedScheduler looks for a config directory in a bucket,
    reads that config and then pulls test_feeds from teh test_feeds.d/ directory in teh same bucket
    '''
    def __init__(self, config_bucket_name=None, config_key=None, schedule_feed=False):
                 #feed_bucket=None, feed_folder=None, es_endpoint=None, feed_archive_bucket=None, es_index=None):
        if config_bucket_name is None:
            config_bucket_name = "elastic_intel_bucket"
        self.config_bucket_name = config_bucket_name
        if config_key is None:
            config_key = "config.json"
        self.config_key = config_key
        self.sns = boto3.client('sns')
        self.s3 = boto3.resource('s3')
        #self.s3.Bucket(self.config_bucket_name).download_file('config/config.json.bak', '/tmp/config.json.bak')
        self.intel_bucket = self.s3.Bucket(self.config_bucket_name)
        self.intel_bucket.download_file('config/config.json', '/tmp/config.json')
        with open("/tmp/config.json", "r") as configfile:
            self.config = json.load(configfile)
        self.schedule_feed = schedule_feed

    def get_feeds(self):
        '''
        if using s3:
            copy *.json from s3 folder to /tmp/test_feeds.d/
        if using local:
            read *.json from /test_feeds.d/
        :return:
        '''
        feeds = []
        feed_keys = [i.key for i in self.intel_bucket.objects.all() if i.key.startswith("feeds.d/") and i.key.endswith("json")]
        try:
            os.mkdir("/tmp/feeds.d")
        except Exception as e:
            print("meh")
        for feed_key in feed_keys:
            self.intel_bucket.download_file(feed_key, "/tmp/"+feed_key)
        feed_dir = "/tmp/feeds.d/"
        feed_files = [i for i in os.listdir(feed_dir) if i.endswith("json")]
        print(feed_files)
        for feed_file in feed_files:
            feed_path = os.path.join(feed_dir, feed_file)
            with open(feed_path, "r") as feeds_json:
                feeds_dict = json.load(feeds_json)
                for feed in feeds_dict['feeds'] :
                    if feed['feed_name'] != '':
                        feeds.append(feed)
        return feeds

    def schedule_feeds(self, feed_list):
        '''
        read list of test_feeds and kick off lambdas for those that need running
        :param feed_list:
        :return:
        '''
        hour = int(datetime.now().strftime("%H"))
        print("current hour is: {}".format(hour))
        for feed in feed_list:
            if self.schedule_feed:
                if self.schedule_feed == "all":
                    print("{} scheduled for ingest".format(feed['feed_name']))
                    resp = self.invoke_feed_lambda(feed)
                    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
                        print(resp)
                else:
                    if feed['feed_name'] == self.schedule_feed:
                        print("{} scheduled for ingest".format(feed['feed_name']))
                        resp = self.invoke_feed_lambda(feed)
                        if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
                            print(resp)
            elif hour in feed['check_interval']:
                print("{} scheduled for ingest".format(feed['feed_name']))
                resp = self.invoke_feed_lambda(feed)
                if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
                    print(resp)


    def invoke_feed_lambda(self, feed):
        '''
        invoke lambda with feed params
        :param feed:
        :return:
        '''
        event = {}
        event.update(self.config)
        event['feed'] = feed
        event['bucket_name'] = self.config_bucket_name
        topic_arn = os.environ['INTEL_SNS_TOPIC_ARN']
        resp = self.sns.publish(TargetArn=topic_arn,
                         Message=json.dumps({'default': json.dumps(event)}),
                         MessageStructure='json'
                         )
        return resp

    def cleanup(self):
        shutil.rmtree("/tmp/feeds.d")

def handler(event, context):
    '''
    lambda handler
    :param event:
    :param context:
    :return:
    '''
    print(os.environ['INTEL_BUCKET_NAME'])
    bucket_name = os.environ['INTEL_BUCKET_NAME']
    print(event)
    if "schedule_feed" in event.keys():
        print(event['schedule_feed'])
        if event["schedule_feed"]:
            feedscheduler = FeedScheduler(bucket_name, schedule_feed=event['schedule_feed'])
        else:
            feedscheduler = FeedScheduler(bucket_name)
    else:
        feedscheduler = FeedScheduler(bucket_name)
    feeds = feedscheduler.get_feeds()
    feedscheduler.schedule_feeds(feeds)
    feedscheduler.cleanup()
    #print(feedscheduler.get_feeds())



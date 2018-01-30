#!/usr/bin/env python3
import boto3
import json
import os
import argparse
import configparser
import shutil
import pytest
from helpers.terraform import TerraformHelper
from helpers.feedhelper import FeedHelper



class ElasticIntel(object):
    def __init__(self, config_bucket_name=None, config_key=None):
        '''
        init things
        '''
        # feed_bucket=None, feed_folder=None, es_endpoint=None, feed_archive_bucket=None, es_index=None):
        if config_bucket_name is None:
            config_bucket_name = "elastic_intel_bucket"
        self.config_bucket_name = config_bucket_name
        if config_key is None:
            config_key = "config.json"
        self.project_dir = os.path.abspath(os.curdir)
        self.config_key = config_key
        self.sns = boto3.client('sns')
        self.s3 = boto3.resource('s3')
        # self.s3.Bucket(self.config_bucket_name).download_file('config/config.json.bak', '/tmp/config.json.bak')
        self.intel_bucket = self.s3.Bucket(self.config_bucket_name)
        self.intel_bucket.download_file('config/config.json', '/tmp/config.json')
        with open("/tmp/config.json", "r") as configfile:
            self.config = json.load(configfile)

    def list_all_feeds(self):
        def get_feeds():
            """
            Copy all test_feeds in test_feeds.d directory (from s3) and read return all feed names/schedule
            :return:
            """
            feeds = []
            feed_keys = [i.key for i in self.intel_bucket.objects.all() if
                         i.key.startswith("test_feeds.d/") and i.key.endswith("json")]
            try:
                shutil.rmtree("/tmp/test_feeds.d")
            except:
                pass
            try:
                os.mkdir("/tmp/test_feeds.d")
            except Exception as e:
                print(e)
            for feed_key in feed_keys:
                self.intel_bucket.download_file(feed_key, "/tmp/" + feed_key)
            feed_dir = "/tmp/test_feeds.d/"
            feed_files = [i for i in os.listdir(feed_dir) if i.endswith("json")]
            for feed_file in feed_files:
                feed_path = os.path.join(feed_dir, feed_file)
                with open(feed_path, "r") as feeds_json:
                    feeds_dict = json.load(feeds_json)
                    for feed in feeds_dict['test_feeds']:
                        if feed['feed_name'] != '':
                            feeds.append(feed)
            return feeds
        feeds = get_feeds()
        for feed in feeds:
            if len(feed) > 0:
                print('Feed: \n\t"{} \n\tSchedule: {}'.format(feed['feed_name'], feed['check_interval']))





def main():
    parser = argparse.ArgumentParser()
    config = configparser.ConfigParser()
    config.read("config.conf")
    parser.add_argument('-env', '--environment', help='Working environment (Dev || Prod).  If not specified, defaults to Dev',
                     default='dev')
    parser.add_argument('--create', help='create infrastructure.  Requires at least one additional argument, the component(s) to '
                                         'be created.  Options: --all, --elastic, --s3, --sns --lambda', action='store_true')
    parser.add_argument('--destroy', help='destroy infrastructure Requires at least one additional argument, the component(s) to '
                                         'destroy.  Options: --all, --elastic, --s3, --sns --lambda', action='store_true')
    parser.add_argument('--plan', help='plan deployment, but do not create', action='store_true', default=False)
    parser.add_argument('--elastic', help='create, destroy or update elastic search component of infrastructure', action='store_true')
    parser.add_argument('--aws_lambda', help='create, destroy or update lambda component of infrastructure', action='store_true')
    parser.add_argument('--s3', help='create, destroy or update s3 component of infrastructure', action='store_true')
    parser.add_argument('--sns', help='create, destroy or update sns component of infrastructure', action='store_true')
    parser.add_argument('--all', help='create, destroy or update all components of infrastructure', action='store_true')
    parser.add_argument('--test_feeds', help='create, destroy or update test_feeds', action='store_true')
    parser.add_argument('--list_feeds', help='list all intel test_feeds that are configured in s3', action='store_true')
    parser.add_argument('--test', help='run tests based on specified flags', action='store_true')
    parser.add_argument('--feed', help='specify a feed by name. EG "my tests feed".  Note:  Must be passed within double quotes')
    parser.add_argument('--update_feeds', help='update feeds', action='store_true')
    parser.add_argument('--whois_lambda', help='update whois lambdas', action='store_true')
    parser.add_argument('--intel_bot', help='create, destory or update intelbot component', action='store_true')
    parser.add_argument('--update_backends',  help='update s3 backend configs', action='store_true')
    args = parser.parse_args()
    env = args.environment
    #elasticintel = ElasticIntel(config_bucket_name="my_test_intel_bucket2")
    ####Create logic
    tf_helper = TerraformHelper(environment=env)
    if args.create:
        tf_helper.init_backends(env=env)
        if args.elastic:
            print("plan set to: {}".format(args.plan))
            tf_helper.up_elasticsearch(plan=args.plan)
        if args.s3:
            tf_helper.up_s3(config[args.environment]['intel_bucket_name'])
        if args.sns:
            tf_helper.up_sns(plan=args.plan)
        if args.aws_lambda:
            tf_helper.up_lambda(plan=args.plan)
        if args.whois_lambda:
            tf_helper.up_whois_lambda()
        if args.intel_bot:
            tf_helper.up_intel_bot()
        if args.all:
            tf_helper.up_elasticsearch(plan=args.plan)
            tf_helper.up_s3(config[args.environment]['intel_bucket_name'])
            tf_helper.up_sns(plan=args.plan)
            tf_helper.up_lambda(plan=args.plan)
            tf_helper.up_whois_lambda()
            tf_helper.up_feeds()
    if args.update_feeds:
        tf_helper.up_feeds()
    if args.destroy:
        ans = input("You are about to destroy resources.  Are you sure you want to do this?\n"
                    "if so, please enter 'I AGREE': ")
        if ans == "I AGREE":
            tf_helper = TerraformHelper(environment=env)
            if args.elastic:
                es_ans = input("NOTE:  YOU ARE ABOUT TO DESTROY YOUR ELASTIC SEARCH INSTANCE.  ANY DATA IT CONTAINS\n"
                               "WILL ALSO BE LOST.  TO DESTROY, PLEASE ENTER 'DESTROY ELASTICSEARCH'")
                if es_ans == "DESTROY ELASTICSEARCH":
                    tf_helper.down_elasticsearch()
            if args.s3:
                tf_helper.down_s3(config[args.environment]['intel_bucket_name'])
            if args.sns:
                tf_helper.down_sns()
            if args.aws_lambda:
                tf_helper.down_lambda()
            if args.whois_lambda:
                tf_helper.down_whois_lambda()
            if args.all:
                tf_helper.down_lambda()
                tf_helper.down_sns()
                tf_helper.down_s3(config[args.environment]['intel_bucket_name'])
                es_ans = input("NOTE:  YOU ARE ABOUT TO DESTROY YOUR ELASTIC SEARCH INSTANCE.  ANY DATA IT CONTAINS\n"
                               "WILL ALSO BE LOST.  TO DESTROY, PLEASE ENTER: 'DESTROY ELASTICSEARCH' \n")
                if es_ans == "DESTROY ELASTICSEARCH":
                    tf_helper.down_elasticsearch()
    if args.list_feeds:
        elasticintel = ElasticIntel(config_bucket_name=config[args.environment]['intel_bucket_name'])
        print(elasticintel.list_all_feeds())
    if args.test:
        os.chdir('tests')
        if args.test_feeds:
            pytest.main(['test_feeds.py'])
            return
        if args.aws_lambda:
            pytest.main(['test_ioc_parser.py'])
    if args.update_backends:
        tf_helper.init_backends(env=env)

if __name__ == '__main__':
    main()


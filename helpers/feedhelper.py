#!/usr/bin/env python3
import json
import os

from helpers.feed_mgr import FeedManager


class FeedHelper(object):
    def __init__(self):
        test_event = {
            "es_endpoint": "test_endpoint",
            "intel_index": "test_index"
        }
        self.fm = FeedManager(event=test_event)

    def get_feed_dict(self, feed_name):
        '''
        searches test_feeds folder for named feed and returns feed dict
        :param feed_name:
        :return:
        '''
        for filename in os.listdir("test_feeds.d"):
            with open(os.path.join("test_feeds.d", filename), "r") as openfile:
                data = json.load(openfile)
                for feed in data['test_feeds']:
                    if feed['feed_name'] == feed_name:
                        return feed
        return

    def test_feed(self, feed_name):
        '''
        takes in a feed name.  If that feed name is found in teh test_feeds.d/
        directory, tests will attempt to get data from teh feed url, parse the
        data and print out tests data to verify it is working as intended
        :param feed_name:
        :return:
        '''
        print("Attempting to parse feed dict...")
        feed_dict = self.get_feed_dict(feed_name)
        if feed_dict:
            print("Success!")
        print("Trying to retrieve list from {}...".format(feed_dict['feed_url']))
        feed_data = self.fm.get_feed(feed_dict)
        if feed_data:
            print("Successfully retrieved feed")
            print("length of feed data: {}".format(len(feed_data)))
        print("Now attempting to parse feed data...")
        print("Parsing data as {}...".format(feed_dict['feed_type']))
        print("Data returned {} lines".format(len(feed_data.split("\n"))))
        feed_results = self.fm.parse_feed(feed_data, feed_dict)
        #feed_results = self.fm.parse_feed(self.fm.get_feed(feed_dict), feed_dict)
        print("{} returned {} indicators".format(feed_name, len(feed_results)))
        print("sample indicators..\n")
        for i in feed_results[:2]:
            summary_dict = {}
            for k in i.intel_dict.keys():
                if i.intel_dict[k]:
                    summary_dict[k] = i.intel_dict[k]
            print(summary_dict)
            print()
        return feed_results


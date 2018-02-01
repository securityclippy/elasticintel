import json
import pytest
import os

def  test_feeds_have_name():
    for i in os.listdir("feeds.d"):
        if i.endswith(".json"):
            with open("feeds.d/{}".format(i), "r") as infile:
                data = json.load(infile)
            for feed in data['feeds']:
                assert len(feed['feed_name']) >= 1

def test_feeds_have_type():
    for i in os.listdir("feeds.d"):
        if i.endswith(".json"):
            with open("feeds.d/{}".format(i), "r") as infile:
                data = json.load(infile)
            for feed in data['feeds']:
                print(feed['feed_name'])
                print("feeds.d/{}".format(i))
                if feed['feed_type'] == 'txt' or feed['feed_type'] == 'csv':
                    is_txt_or_csv = True
                else:
                    is_txt_or_csv = False
                assert is_txt_or_csv == True

def test_csv_feeds():
    csv_feeds = []
    for i in os.listdir("feeds.d"):
        if i.endswith(".json"):
            with open("feeds.d/{}".format(i), "r") as infile:
                data = json.load(infile)
            for feed in data['feeds']:
                if feed['feed_type'] == "csv":
                    csv_feeds.append(feed)
    for feed in csv_feeds:
        print(feed['feed_name'])
        assert 'feed_url' in feed.keys()
        assert 'feed_name' in feed.keys()
        assert 'feed_type' in feed.keys()
        assert 'indicator_type' in feed.keys()
        assert 'check_interval' in feed.keys()
        assert 'field_mapping' in feed.keys()
        assert 'separator' in feed['field_mapping'].keys()
        assert 'source' in feed['field_mapping'].keys()
        assert 'destination' in feed['field_mapping'].keys()
        assert 'has_headers' in feed['field_mapping'].keys()


def test_txt_feeds():
    txt_feeds = []
    for i in os.listdir("feeds.d"):
        if i.endswith(".json"):
            with open("feeds.d/{}".format(i), "r") as infile:
                data = json.load(infile)
            for feed in data['feeds']:
                if feed['feed_type'] == "txt":
                    txt_feeds.append(feed)
    for feed in txt_feeds:
        print(feed['feed_name'])
        assert 'feed_url' in feed.keys()
        assert 'feed_name' in feed.keys()
        assert 'feed_type' in feed.keys()
        assert 'indicator_type' in feed.keys()
        assert 'check_interval' in feed.keys()


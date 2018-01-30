import pytest
import json
import pandas
#from elasticintel.ingest_feed_lambda.ioc_feed_parser import IOCFeedParser
from ingest_feed_lambda.ioc_feed_parser import IOCFeedParser
#from ingest_feed_lambda.ioc_feed_parser import IOCFeedParser

@pytest.fixture
def txt_feed_dict():
    with open("test_feeds/txt_feed.json", "r") as infile:
        feed = json.load(infile)
    return feed

@pytest.fixture
def txt_feed_data():
    with open("test_feeds/test_txt_data.txt", "r") as infile:
        feed_data = infile.read()
    return feed_data


@pytest.fixture
def csv_feed_dict():
    with open("test_feeds/csv_feed.json", "r") as infile:
        feed = json.load(infile)
    return feed

@pytest.fixture
def csv_test_data():
    with open("test_feeds/test_csv_data.txt", "r") as infile:
        feed_data = infile.read()
    return feed_data

def test_feed_has_url():
    feed = txt_feed_dict()
    assert 'feed_url' in feed.keys()

def test_feed_has_feed_name():
    feed = txt_feed_dict()
    assert 'feed_name' in feed.keys()

def test_feed_has_indicator_type():
    feed = txt_feed_dict()
    assert 'indicator_type' in feed.keys()

def test_parse_feed_type():
    txt_feed = txt_feed_dict()
    csv_veed = csv_feed_dict()



def test_clean_csv_feed():
    feed = csv_feed_dict()
    data = csv_test_data()
    fp = IOCFeedParser("")
    cleaned_feed = fp.clean_feed(data, feed)
    #print(cleaned_feed)
    for line in cleaned_feed.split("\n"):
        line_len = len(line.split(feed['field_mapping']['separator']))
        source_len = len(feed['field_mapping']['source'])
        assert line_len == source_len

def test_csv_has_source():
    iocparser = IOCFeedParser("event")
    parsed_csv = iocparser.parse_csv(csv_test_data(), csv_feed_dict())
    assert 'source' in parsed_csv.columns

def test_csv_has_indexed_at():
    iocparser = IOCFeedParser("event")
    parsed_csv = iocparser.parse_csv(csv_test_data(), csv_feed_dict())
    assert 'indexed_at' in parsed_csv.columns

def test_parse_csv_adds_headers():
    iocparser = IOCFeedParser("event")
    parsed_csv = iocparser.parse_csv(csv_test_data(), csv_feed_dict())
    dest_fields = [i for i in csv_feed_dict()['field_mapping']['destination'] if i is not None]
    dest_fields += ['indexed_at']
    dest_fields += ['source']
    dest_fields += ['indicator_type']
    dest_fields += ['whois']
    dest_fields += ['whois_last_updated']
    assert list(parsed_csv.columns) == dest_fields

def test_process_feeds_is_dataframe():
    fp = IOCFeedParser("")
    feed = txt_feed_dict()
    assert type(fp.process_feed(feed)) == pandas.DataFrame

def test_parse_txt_adds_headers():
    iocparser = IOCFeedParser("event")
    parsed_txt = iocparser.parse_txt(txt_feed_data(), txt_feed_dict())
    assert txt_feed_dict()['indicator_type'] in parsed_txt.columns
    assert 'source' in parsed_txt.columns
    assert 'indexed_at' in parsed_txt.columns
    assert 'indicator_type' in parsed_txt.columns
    assert 'whois' in parsed_txt.columns
    assert 'whois_last_updated' in parsed_txt.columns


import logging
import pandas as pd
import requests
from io import StringIO
from datetime import datetime,  timedelta
import boto3
try:
    from ioc_validators import IOCValidator
except:
    from ingest_feed_lambda.ioc_validators import IOCValidator

logging.basicConfig()
log = logging.getLogger("ioc_feed_parser")
log.setLevel(logging.INFO)

class IOCFeedParser(object):
    def __init__(self, event):
        self.blerp = "blerp"
        self.event = event

    def feed_timestamp(self):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _clean_csv(self, feed_data, feed_dict):
        lines = []
        data = str(feed_data).split("\n")
        source_field_list = feed_dict['field_mapping']['source']
        sep = feed_dict['field_mapping']['separator']
        total_lines = 0
        skipped = 0
        for line in data:
            total_lines += 1
            if len(line.split(sep)) != len(source_field_list):
                skipped += 1
                pass
            else:
                lines.append(line)
        clean_data = "\n".join(lines)
        print("skipped {}/{} lines".format(skipped, total_lines))
        return clean_data

    def _clean_txt(self, feed_data, feed_dict):
        lines = []
        data = str(feed_data).split("\n")
        skipped = 0
        if feed_dict['indicator_type'] == "ipaddress":
            is_valid_indicator = IOCValidator.is_valid_ipaddress
        if feed_dict['indicator_type'] == "url":
            is_valid_indicator = IOCValidator.is_valid_url
        for line in data:
            if line:
                if is_valid_indicator(line.strip()):
                    lines.append(line.strip())
                else:
                  skipped += 1
        clean_data = "\n".join(lines)
        print("skipped {}/{} lines".format(skipped, len(lines)))
        return clean_data

    def clean_feed(self, feed_data, feed_dict):
        '''
        cleans feed data, based on feed type
        :param feed_data:
        :param feed_dict:
        :return:
        '''
        if feed_dict['feed_type'] == 'csv':
            return self._clean_csv(feed_data, feed_dict)
        if feed_dict['feed_type'] == 'txt':
            return self._clean_txt(feed_data, feed_dict)

    def add_common_fields(self, df, feed_dict):
        tstamp = self.feed_timestamp()
        #whois_last_updated = None
        whois_last_updated = (datetime.now() - timedelta(weeks=3)).strftime("%Y-%m-%dT%H:%M:%S")
        source = feed_dict['feed_name']
        if feed_dict['feed_type'] == 'csv':
            df.columns = feed_dict['field_mapping']['destination']
            df = df.assign(indexed_at=tstamp)
            df = df.assign(source=source)
            df = df.assign(indicator_type=feed_dict['indicator_type'])
            df = df.assign(whois="not found")
            df = df.assign(whois_last_updated=whois_last_updated)
            cols = [i for i in feed_dict['field_mapping']['destination'] if i is not None]
            cols += ['indexed_at']
            cols += ['source']
            cols += ['indicator_type']
            cols += ['whois']
            cols += ['whois_last_updated']
            return df[cols]
        if feed_dict['feed_type'] == 'txt':
            df = df.assign(indexed_at=tstamp)
            df = df.assign(source=source)
            df = df.assign(indicator_type=feed_dict['indicator_type'])
            df = df.assign(whois="not found")
            df = df.assign(whois_last_updated=whois_last_updated)
            return df



    def parse_csv(self, csv_data, feed_dict):
        '''
        cleans and parses raw feed data, returns pandas dataframe
        :param txt_data:
        :param feed_dict:
        :return:
        '''
        cleaned_data = self.clean_feed(csv_data,  feed_dict)
        data = StringIO(cleaned_data)
        src = feed_dict['field_mapping']['source']
        select_columns = [src.index(i) for i in src if i is not None]
        if feed_dict['field_mapping']['has_headers']:
            df = pd.read_csv(data, sep=feed_dict['field_mapping']['separator'],
                             usecols=select_columns,
                             error_bad_lines=False)
        else:
            df = pd.read_csv(data, sep=feed_dict['field_mapping']['separator'], header=None,
                             usecols=select_columns,
                             error_bad_lines=False)
        return self.add_common_fields(df, feed_dict)

    def parse_txt(self, txt_data, feed_dict):
        '''
        cleans and parses raw feed data, returns pandas dataframe
        :param txt_data:
        :param feed_dict:
        :return:
        '''
        cleaned_data = self.clean_feed(txt_data, feed_dict)
        df = pd.read_csv(StringIO(cleaned_data), header=None, error_bad_lines=False)
        df.columns = [feed_dict['indicator_type']]
        return self.add_common_fields(df, feed_dict)

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

    def proccess_feed_data(self, feed_data, feed):
        '''
        process raw feed data as csv or txt based on feed type
        calls parse_csv or parse_txt based  on type
        :param feed_data:
        :param feed:
        :return:
        '''
        print("Processing: {}".format(feed['feed_name']))
        if feed['feed_type'] == 'csv':
            print("Processing feed as type: CSV")
            df = self.parse_csv(feed_data, feed)
            return df
        if feed['feed_type'] == 'txt':
            print("Processing feed as type: TXT")
            df = self.parse_txt(feed_data, feed)
            return df
        return False

    def process_feed(self, feed):
        feed_data = self.get_feed(feed)
        cleaned = self.clean_feed(feed_data, feed)
        if feed['feed_type'] == 'csv':
            df = self.parse_csv(cleaned, feed)
            return df
        if feed['feed_type'] == 'txt':
            df = self.parse_txt(cleaned, feed)
            return df
        return False


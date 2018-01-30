from ioc_feed_parser import IOCFeedParser
from es import ES
import json



def handler(event, context):
    '''
    :param event:
    :param context:
    :return:
    '''
    event = json.loads(event['Records'][0]['Sns']['Message'])
    feed = event['feed']
    iocfp = IOCFeedParser(event)
    elasticsearch = ES(es_host=event['es_endpoint'])
    feed_data = iocfp.get_feed(feed)
    parsed_feed = iocfp.proccess_feed_data(feed_data, feed)
    iocfp.save_to_s3(feed_data, feed)
    elasticsearch.bulk_es_index_dataframe(es_index='iocs', df=parsed_feed)


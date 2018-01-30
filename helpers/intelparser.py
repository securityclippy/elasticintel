import logging
from urllib.parse import urlparse

import validators
try:
    from intel import Intel
except:
    from ingest_feed_lambda.intel import Intel
try:
    from intel_validator import is_valid_ip, is_proxy
except:
    from ingest_feed_lambda.intel_validator import is_valid_ip, is_proxy

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class IntelParser(object):
    def __init__(self):
        ''''''

    @staticmethod

    def parse_list(self, list_data, validator):
        '''
        pass data in python list ([]) form.  each item will be validated by the selected validator
        and returned if valid
        :param list_data:
        :param validator:
        :return:
        '''
        if validator == 'ipaddress':
            parsed_list = []
            for item in list_data:
                LOGGER.info(item)
                if is_valid_ip(item):
                    parsed_list.append(item)
            return parsed_list

    @staticmethod
    def parse_feed(feed_data, feed_dict):
        '''
        for csv test_feeds, it is important to note that EVERY field in the line of csv data
        must be mapped between source and destination. Because there may not be a pre-defined
        field for each data type in a csv, if custom field(s) are specified, these fields will
        also appear in the json data in elasticsearch
        :param feed_data:
        :param feed_dict:
        :return:
        '''
        intel_list = []
        #parse csv lists
        if feed_dict['feed_type'] == 'csv':
            if feed_dict['indicator_type'] == 'ipaddress':
                source_field_list = feed_dict['field_mapping']['source']
                destination_field_list = feed_dict['field_mapping']['destination']
                if len(source_field_list) != len(destination_field_list):
                    LOGGER.info("error, field mapping lengths are not the same")
                    LOGGER.info(len(source_field_list))
                    LOGGER.info(len(destination_field_list))
                    exit()
                data = str(feed_data).split("\n")
                for line in data:
                    if len(line.split(",")) != len(destination_field_list):
                        LOGGER.debug("error, line input does not contain required fields")
                        continue
                    # make sure there are no blank entries, skip if there are
                    if "" not in line.split(","):
                        d = {}
                        # LOGGER.info(destination_field_list)
                        # LOGGER.info(line.split(","))
                        for i in range(len(destination_field_list)):
                            # if i == "":
                            d[destination_field_list[i]] = line.split(",")[i].strip()
                        intel_obj = Intel(indicator_type=feed_dict['indicator_type'], source=feed_dict['feed_name'],
                                          intel_dict=d)
                        if intel_obj.validate():
                            LOGGER.debug(intel_obj.to_json())
                            intel_list.append(intel_obj)
                return [i for i in intel_list if type(i) != str]
            if feed_dict['indicator_type'] == 'domain':
                source_field_list = feed_dict['field_mapping']['source']
                destination_field_list = feed_dict['field_mapping']['destination']
                if len(source_field_list) != len(destination_field_list):
                    LOGGER.info("error, field mapping lengths are not the same")
                    LOGGER.info(len(source_field_list))
                    LOGGER.info(len(destination_field_list))
                    exit()
                data = str(feed_data).split("\n")
                for line in data:
                    if len(line.split(",")) != len(destination_field_list):
                        LOGGER.debug("error, line input does not contain required fields")
                        continue
                    # make sure there are no blank entries, skip if there are
                    if "" not in line.split(","):
                        d = {}
                        # LOGGER.info(destination_field_list)
                        # LOGGER.info(line.split(","))
                        for i in range(len(destination_field_list)):
                            # if i == "":
                            d[destination_field_list[i]] = line.split(",")[i].strip()
                        intel_obj = Intel(indicator_type=feed_dict['indicator_type'], source=feed_dict['feed_name'],
                                          intel_dict=d)
                        if intel_obj.validate():
                            LOGGER.debug(intel_obj.to_json())
                            intel_list.append(intel_obj)
                return [i for i in intel_list if type(i) != str]
            if feed_dict['indicator_type'] == 'url':
                source_field_list = feed_dict['field_mapping']['source']
                destination_field_list = feed_dict['field_mapping']['destination']
                if len(source_field_list) != len(destination_field_list):
                    LOGGER.info("error, field mapping lengths are not the same")
                    LOGGER.info(len(source_field_list))
                    LOGGER.info(len(destination_field_list))
                    exit()
                data = str(feed_data).split("\n")
                for line in data:
                    if len(line.split(",")) != len(destination_field_list):
                        LOGGER.debug("error, line input does not contain required fields")
                        continue
                    # make sure there are no blank entries, skip if there are
                    if "" not in line.split(","):
                        d = {}
                        # LOGGER.info(destination_field_list)
                        # LOGGER.info(line.split(","))
                        for i in range(len(destination_field_list)):
                            # if i == "":
                            d[destination_field_list[i]] = line.split(",")[i].strip()
                        intel_obj = Intel(indicator_type=feed_dict['indicator_type'], source=feed_dict['feed_name'],
                                          intel_dict=d)
                        if intel_obj.validate():
                            LOGGER.debug(intel_obj.to_json())
                            intel_list.append(intel_obj)
                return [i for i in intel_list if type(i) != str]
        # parse txt based lists (single column)
        if feed_dict['feed_type'] == 'txt':
            if feed_dict['indicator_type'] == 'ipaddress':
                data = str(feed_data).split("\n")
                for line in data:
                    #don't deal with data if it coudn't possibly be valid
                    if len(line) > 4:
                        line = line.strip()
                        if is_valid_ip(line):
                            d = {}
                            LOGGER.debug(line)
                            d['ipaddress'] = line
                            intel = Intel(indicator_type=feed_dict['indicator_type'],
                                          source=feed_dict['feed_name'], intel_dict=d)
                            LOGGER.debug(d)
                            if intel.validate():
                                LOGGER.debug("Adding intel {}".format(intel.to_json()))
                                intel_list.append(intel)
                            else:
                                LOGGER.debug("invalid intel object")
                        else:
                            LOGGER.debug("Invalid IP: {}".format(line))
                return intel_list
            if feed_dict['indicator_type'] == 'url':
                data = str(feed_data).split("\n")
                for line in data:
                    #don't deal with data if it coudn't possibly be valid
                    if len(line) > 4:
                        line = line.strip()
                        #ignore validation here, because urls are fuckin hardmode
                        #fukin haxor bastids
                        if line:
                        #if bool(urlparse(line).scheme):
                            d = {}
                            d['url'] = line
                            intel = Intel(indicator_type=feed_dict['indicator_type'],
                                          source=feed_dict['feed_name'], intel_dict=d)
                            #if intel.validate():
                            LOGGER.debug("Adding intel {}".format(intel.to_json()))
                            intel_list.append(intel)
                            #else:
                                #LOGGER.debug("BLERP")
                                #LOGGER.debug("Invalid url: {}".format(line))
                        else:
                            LOGGER.debug("Invalid URL: {}".format(line))
                return intel_list
            if feed_dict['indicator_type'] == 'domain':
                data = str(feed_data).split("\n")
                for line in data:
                    #don't deal with data if it coudn't possibly be valid
                    if len(line) > 4:
                        line = line.strip()
                        if validators.domain(line):
                            d = {}
                            d['domain'] = line
                            intel = Intel(indicator_type=feed_dict['indicator_type'],
                                          source=feed_dict['feed_name'], intel_dict=d)
                            if intel.validate():
                                LOGGER.debug("Adding intel {}".format(intel.to_json()))
                                intel_list.append(intel)
                            else:
                                LOGGER.debug("BLERP")
                                LOGGER.debug("Invalid url: {}".format(line))
                        else:
                            LOGGER.debug("Invalid URL: {}".format(line))
                return intel_list
            if feed_dict['indicator_type'] == 'proxy':
                data = str(feed_data).split("\n")
                for line in data:
                    #don't deal with data if it coudn't possibly be valid
                    if len(line) > 4:
                        line = line.strip()
                        if is_proxy(line):
                            d = {}
                            d['proxy'] = line
                            intel = Intel(indicator_type=feed_dict['indicator_type'],
                                          source=feed_dict['feed_name'], intel_dict=d)
                            if intel.validate():
                                LOGGER.debug("Adding intel {}".format(intel.to_json()))
                                intel_list.append(intel)
                            else:
                                LOGGER.debug("Invalid proxy: {}".format(line))
                        else:
                            LOGGER.debug("Invalid proxy: {}".format(line))
            return [i for i in intel_list if type(i) != str]
        if feed_dict['feed_type'] == 'threatexchange':
            print("Threat Exchange")
            if feed_dict['indicator_type'] == 'ipaddress':
                #feed will be in list format
                for indicator in feed_data:
                    d = {}
                    d['ipaddress'] = indicator['indicator']['indicator']
                    try:
                        d['description'] = indicator['description']
                        d['created'] = indicator['added_on']
                    except KeyError:
                        pass
                    intel = Intel(indicator_type=feed_dict['indicator_type'],
                                  source=feed_dict['feed_name'], intel_dict=d)
                    if intel.validate():
                        LOGGER.info("Adding intel {}".format(intel.to_json()))
                        intel_list.append(intel)
                    else:
                        LOGGER.info("Invalid proxy: {}".format(intel.ipaddress))
            return [i for i in intel_list if type(i) != str]

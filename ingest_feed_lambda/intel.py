#!/usr/bin/env python3
import json
from urllib.parse import urlparse
import validators
import logging
import datetime
try:
    from intel_validator import is_valid_ip, is_md5, is_sha1, is_sha256, is_valid_port, is_proxy
except:
    from ingest_feed_lambda.intel_validator import is_valid_ip, is_md5, is_sha1, is_sha256, is_valid_port, is_proxy

logging.basicConfig()
LOGGER = logging.getLogger('parser')
LOGGER.setLevel(logging.DEBUG)


class Intel(object):
    def __init__(self, indicator_type, source, intel_dict):
        intel_keys = intel_dict.keys()
        self.intel_dict = intel_dict
        self.submission_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        self.feed_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if 'ipaddress' in intel_keys:
            self.ipaddress = intel_dict['ipaddress']
        else:
            self.ipaddress = ""
        if 'domain' in intel_keys:
            self.domain = intel_dict['domain']
        else:
            self.domain = ""
        if 'url' in intel_keys:
            self.url = intel_dict['url']
        else:
            self.url = ""
        if 'domain_usage' in intel_keys:
            self.domain_usage = intel_dict['domain_usage']
        else:
            self.domain_usage = ""
        if 'description' in intel_keys:
            self.description = intel_dict['description']
        else:
            self.description = ""
        if 'md5_hash' in intel_keys:
            self.md5_hash = intel_dict['md5_hash']
        else:
            self.md5_hash = ""
        if 'sha1_hash' in intel_keys:
            self.sha1_hash = intel_dict['sha1_hash']
        else:
            self.sha1_hash = ""
        if 'sha256' in intel_keys:
            self.sha256_hash = intel_dict['sha256_hash']
        else:
            self.sha256_hash = ""
        if 'src_port' in intel_keys:
            self.src_port = intel_dict['src_port']
        else:
            self.src_port = ""
        if 'dst_port' in intel_keys:
            self.dst_port = intel_dict['dst_port']
        else:
            self.dst_port = ""
        if 'proxy' in intel_keys:
            self.proxy = intel_dict['proxy']
        else:
            self.proxy = ""
        if 'country' in intel_keys:
            self.country = intel_dict['country']
        else:
            self.country = ""
        if 'region' in intel_keys:
            self.region = intel_dict['region']
        else:
            self.region = ""
        if 'city' in intel_keys:
            self.city = intel_dict['region']
        else:
            self.city = ""
        if 'whois' in intel_keys:
            self.whois = intel_dict['whois']
        else:
            self.whois = ""
        if 'source' in intel_keys:
            self.source = intel_dict['source']
        else:
            self.source = source
        self.indicator_type = indicator_type

    def validate(self):
        if self.indicator_type not in ["ipaddress", "domain", "hash", "url", "proxy"]:
            LOGGER.debug("Invalid indicator type: {}".format(self.indicator_type))
            return False
        if self.ipaddress != "":
            if not is_valid_ip(self.ipaddress):
                LOGGER.debug("Invalid ipaddress: {}".format(self.ipaddress))
                return False
        if self.domain != "":
            if not validators.domain(self.domain):
                LOGGER.debug("Invalid domain: {}".format(self.domain))
                return False
        if self.url != "":
            if not bool(urlparse(self.url).scheme):
                LOGGER.debug("Invalid url: {}".format(self.url))
                return False
        if self.md5_hash != "":
            if not is_md5(self.md5_hash):
                LOGGER.debug("Invalid md5 hash: {}".format(self.md5_hash))
                return False
        if self.sha1_hash != "":
            if not is_sha1(self.sha1_hash):
                LOGGER.debug("Invalid sh1_hash: {}".format(self.sha1_hash))
                return False
        if self.sha256_hash != "":
            if not is_sha256(self.sha256_hash):
                LOGGER.debug("Invalid sha256_hash: {}".format(self.sha256_hash))
                return False
        if self.src_port != "":
            if not is_valid_port(int(self.src_port)):
                LOGGER.debug("Invalid src_port: {}".format(self.src_port))
                return False
        if self.dst_port != "":
            if not is_valid_port(int(self.dst_port)):
                LOGGER.debug("Invalid dst_port: {}".format(self.dst_port))
                return False
        if self.proxy != "":
            if not is_proxy(self.proxy):
                LOGGER.debug("Invalid proxy: {}".format(self.proxy))
        return True

    def to_dict(self):
        self.intel_dict['indicator_type'] = self.indicator_type
        self.intel_dict['ipaddress'] = self.ipaddress
        self.intel_dict['domain'] = self.domain
        self.intel_dict['domain_usage'] = self.domain_usage
        self.intel_dict['description'] = self.description
        self.intel_dict['url'] = self.url
        self.intel_dict['md5_hash'] = self.md5_hash
        self.intel_dict['sha1_hash'] = self.sha1_hash
        self.intel_dict['sha256_hash'] = self.sha256_hash
        self.intel_dict['src_port'] = self.src_port
        self.intel_dict['dst_port'] = self.dst_port
        self.intel_dict['proxy'] = self.proxy
        self.intel_dict['source'] = self.source
        self.intel_dict['submission_timestamp'] = self.submission_timestamp
        self.intel_dict['feed_date'] = self.feed_date
        self.intel_dict['country'] = self.country
        self.intel_dict['region'] = self.region
        self.intel_dict['city'] = self.city
        self.intel_dict['whois'] = self.whois
        return self.intel_dict

    def to_json(self):
        return json.dumps(self.to_dict())




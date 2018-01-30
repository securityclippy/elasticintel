#!/usr/bin/env python3
'''
Lambda function handler for entry into lambdabot
'''

import os
from iocsearch import IOCSearch

from intelbot import LambdaBot
from iocsearch_lambda import IOCRequest, return_results


def handler(event, context):
    '''
    :param event:
    :param context:
    :return:
    '''
    # Note: This is hear to provide a simple way to verify
    # your function when you set up your slack bot.  Dont't remove
    #this unless you're intending to solve this a different way
    if "challenge" in event:
        return event["challenge"]
    else:
        print("incoming msg: {}".format(event))
        #instantiate bot and do things!
        bot = LambdaBot(botname=os.environ['BOT_NAME'])
        if not bot.process_event(event):
            print("event processing failed, exiting")
            return
        #make sure bot is really supposed to reply
        if bot.is_dm() or bot.has_bot_mention():
            if not bot.is_bot_msg():
                if 'test' in bot.event.event.text:
                    bot.maze_reply()
                    return

                #### Intel Bot routing
                es_host = os.environ['ES_HOST']
                print("ES: {}".format(es_host))
                event_txt = bot.event.event.text
                print("Bot message: {}".format(event_txt))
                if "ipaddress" in event_txt:
                    if "summary" in event_txt:
                        search_data = event_txt.split("summary")[1]
                        strings = search_data.split(",")
                        for string in strings:
                            iocs = IOCSearch(es_instance_host=es_host, is_lambda=True)
                            search_string = string.split("summary")[1].strip()
                            bot.reply_to_user("searching for: {}".format(search_string))
                            ans = iocs.ip_summary(search_string)
                            msg = "got: {} hits for {}.\n Unique Sources: \n{}".format(
                                ans['hits']['total'],
                                search_string,
                                [i['key'] for i in ans['aggregations']['sources']['buckets']]
                            )
                            bot.reply_to_user(msg)
                        return
                    else:
                        search_data = event_txt.split("summary")[1]
                        strings = search_data.split(",")
                        for string in strings:
                            iocs = IOCSearch(es_instance_host=es_host, is_lambda=True)
                            search_string = string.split("summary")[1].strip()
                            print(type(search_string))
                            bot.reply_to_user("searching for: {}".format(search_string))
                            ans = iocs.ip_details(search_string)
                            bot.reply_to_user(ans)
                        return
                if "stringsearch" in event_txt:
                    iocs = IOCSearch(es_instance_host=es_host, is_lambda=True)
                    if "summary" in event_txt:
                        search_data = event_txt.split("summary")[1]
                        strings = search_data.split(",")
                        for string in strings:
                            print("Running string search on: {}".format(string))
                            search_string = string.strip()
                            print(type(search_string))
                            bot.reply_to_user("searching for: {}".format(search_string))
                            ans = iocs.stringsearch_summary(search_string)
                            msg = "```got: {} hits for {}.\n Unique Sources: \n{}```".format(
                                ans['hits']['total'],
                                search_string,
                                [i['key'] for i in ans['aggregations']['sources']['buckets']]
                            )
                            bot.reply_to_user(msg)
                    else:
                        search_data = event_txt.split("stringsearch")[1]
                        strings = search_data.split(",")
                        for string in strings:
                            print("Running string search..")
                            search_string = string.strip()
                            print(type(search_string))
                            bot.reply_to_user("searching for: {}".format(search_string))
                            ans = iocs.stringsearch(search_string)
                            print(ans)
                            bot.reply_to_user(ans)

                    return
                if 'domain' in event_txt:
                    iocs = IOCSearch(es_instance_host=es_host, is_lambda=True)
                    if 'summary' in event_txt:
                        search_data = event_txt.split("summary")[1]
                        strings = search_data.split(",")
                        for string in strings:
                            print(string)
                            search_string = string.strip().split("|")[1]
                            search_string = search_string.strip(">")
                            search_string = search_string.strip("<")
                            print(type(search_string))
                            bot.reply_to_user("searching for: {}".format(search_string))
                            ans = iocs.domain_summary(search_string)
                            msg = "```got: {} hits for {}.\n Unique Sources: \n{}```".format(
                                ans['hits']['total'],
                                search_string,
                                [i['key'] for i in ans['aggregations']['sources']['buckets']]
                            )
                            bot.reply_to_user(msg)
                        return
                    else:
                        search_data = event_txt.split("domain")[1]
                        strings = search_data.split(",")
                        for string in strings:
                            msg = ""
                            search_string = string.strip().split("|")[1]
                            search_string = search_string.strip(">")
                            search_string = search_string.strip("<")
                            bot.reply_to_user("searching for: {}\n".format(search_string))
                            ans = iocs.domain_details(search_string)
                            for i in ans['hits']['hits']:
                                msg += "\n"
                                msg += "```{}\n```".format(i['_source'])
                            msg += "\n"
                            bot.reply_to_user(msg)
                        return
                else:
                    bot.dummy_response()
                return
        return

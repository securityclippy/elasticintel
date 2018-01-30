#!/usr/bin/env python3

'''
simple slack chatbot built to run in aws lambda functions
'''


import json
import re
import boto3
import requests

class Event(object):
    '''
    inner event of a slack event message
    '''
    def __init__(self, slack_event=None):
        if slack_event:
            self.type = slack_event['type']
            if 'user' in slack_event.keys():
                self.user = slack_event['user']
            if 'username' in slack_event.keys():
                self.username = slack_event['username']
            self.text = slack_event['text']
            self.ts = slack_event['ts']
            self.channel = slack_event['channel']
            self.event_ts = slack_event['event_ts']
            if 'bot_id' in slack_event.keys():
                self.bot_id = slack_event['bot_id']
            else:
                self.bot_id = ""
        else:
            self.type = None
            self.user = None
            self.text = None
            self.ts = None
            self.channel = None
            self.event_ts = None
            self.bot_id = None

class SlackBotMessage(object):
    '''
    meta attributes of slack message
    '''
    def __init__(self, event=None):
        if event:
            self.event = Event(event['event'])
            self.token = event['token']
            self.team_id = event['team_id']
            self.api_app_id = event['api_app_id']
            self.type = event['type']
            self.event_id = event['event_id']
            self.event_time = event['event_time']
            self.authed_users = event['authed_users']
            self.has_challenge = False
            if "challege" in event:
                self.has_challenge = True
        else:
            self.event = Event()
            self.token = ""
            self.team_id = ""
            self.api_app_id = ""
            self.type = ""
            self.event_id = ""
            self.event_time = ""
            self.authed_users = ""
            self.has_challenge = False


class LambdaBot(object):
    '''
    Lambdabot object
    '''
    def __init__(self,
                 botname,
                 region_name='us-east-1',
                 #ssm_parameter_name='{}_bot_token'.format(bot),
                 #verification_token_param_name='lambda_bot_verification_token',
                 bot_token=None,
                 verification_token=None,
                 is_lambda=True
                ):
        '''

        :param botname: string, required
        :param region_name: defaults to us-east-1
        :param ssm_parameter_name: defaults to lambda_bot_token
        :param verification_token_param_name: defaults to lambda_bot_verification_token
        :param bot_token: defaults to None, only used for testing
        :param verification_token: defaults to None, only used for testing
        :param is_lambda: defaults to True, indicating bot is running in lambda.  used for testing
        '''

        self.post_message_url = "https://slack.com/api/chat.postMessage"
        ssm = boto3.client('ssm', region_name=region_name)
        if bot_token is None:
            bot_token = ssm.get_parameters(Names=["{}_bot_token".format(botname)],
                                           WithDecryption=True)['Parameters'][0]['Value']
        self.bot_token = bot_token
        if verification_token is None:
            verification_token = ssm.get_parameters(Names=["{}_bot_verification_token".format(botname)],
                                                    WithDecryption=True)['Parameters'][0]['Value']
        self.verification_token = verification_token
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer {}'.format(self.bot_token)}
        self.session = requests.session()
        self.session.headers = self.headers
        self.event = SlackBotMessage()
        self.botname = botname
        self.raw_event = ""
        self.id = ""
        if is_lambda:
            self._get_bot_id()

    def verify_msg(self):
        '''
        verify processed message against verification token
        :return:
        '''
        if self.event.token != self.verification_token:
            print("token mismatch")
            return False
        return True

    @staticmethod
    def _handle_resp(resp):
        j_dict = json.loads(resp.text)
        return j_dict['ok']


    def _get_bot_id(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer {}".format(self.bot_token)
        }
        ans = json.loads(requests.get("https://slack.com/api/users.list", headers=headers).text)
        for i in ans['members']:
            if i['name'] == self.botname:
                self.id = i['id']

    def is_bot_msg(self):
        '''
        return true if processed msg was sent by a bot
        :return:
        '''
        if self.event.event.bot_id:
            return True
        return False

    def is_dm(self):
        '''
        return true if processed message was sent as a direct message
        :return:
        '''
        if self.event.event.channel.startswith("D"):
            return True
        return False

    def has_bot_mention(self):
        '''
        return true if the bot was mentioned in teh text of a message
        :return:
        '''
        if re.search(self.id, self.event.event.text):
            self.event.event.text = self.event.event.text.replace("<@{}>".format(self.id), '')
            print("Bot mentioned, replying...")
            return True
        print('Bot not mentioned, skipping...')
        return False

    def process_event(self, event):
        '''
        process teh event recieved from the api gateway.  this is the main entry point into our bot
        :param event:
        :return:
        '''
        self.raw_event = event
        self.event = SlackBotMessage(event)
        if not self.verify_msg():
            return False
        return True

    def dummy_response(self):
        '''
        simply reverses the message sent and sends it back
        :return:
        '''
        response = {
            "text": self.event.event.text[::-1],
            "channel": self.event.event.channel,
        }
        self._handle_resp(self._post_message(response))

    def _post_message(self, msg_dict):
        '''
        internal method to post to slack API
        :param msg_dict:
        :return:
        '''
        resp = self.session.post(self.post_message_url, data=json.dumps(msg_dict))
        return resp

    def respond_with(self, response):
        '''
        takes in a dictionary of response data and posts to slack api
        :param response:
        :return:
        '''
        self._handle_resp(self._post_message(response))

    def reply_to_user(self, msg):
        '''
        replies to a user ith a specified message
        :param msg: string
        :return:
        '''
        data = {
            "text": msg,
            "channel": self.event.event.channel,
            "as_user": False,
            "attachments": []
        }
        self._handle_resp(self._post_message(data))

    def maze_reply(self):
        '''
        A test response to demonstrate advanced usage
        :return:
        '''
        data = {
            "text": "Would you like to play a game?",
            "channel": self.event.event.channel,
            "attachments": [
                {
                    "text": "Choose a game to play",
                    "fallback": "You are unable to choose a game",
                    "callback_id": "wopr_game",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "game",
                            "text": "Chess",
                            "type": "button",
                            "value": "chess"
                        },
                        {
                            "name": "game",
                            "text": "Falken's Maze",
                            "type": "button",
                            "value": "maze"
                        },
                        {
                            "name": "game",
                            "text": "Thermonuclear War",
                            "style": "danger",
                            "type": "button",
                            "value": "war",
                            "confirm": {
                                "title": "Are you sure?",
                                "text": "Wouldn't you prefer a good game of chess?",
                                "ok_text": "Yes",
                                "dismiss_text": "No"
                            }
                        }
                    ]
                }
            ]
        }
        self._handle_resp(self._post_message(data))

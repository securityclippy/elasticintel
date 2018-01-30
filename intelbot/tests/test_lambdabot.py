from pytest import fixture
from lambda_function.lambdabot import LambdaBot
import json
import requests

import os

os.environ['AWS_ACCESS_KEY_ID'] = "derp"
os.environ['AWS_SECRET_ACCESS_KEY'] = "merp"


class dummy_response(object):
    def __init__(self, text):
        self.text = text

@fixture
def bot():
    return LambdaBot('testbot', is_lambda=False, verification_token='test_token', bot_token='test_bot_token')

@fixture
def user_event():
    with open("tests/test_user_event.json", "r") as f:
        event = json.load(f)
    return event

@fixture
def bot_event():
    with open("tests/test_bot_mesage.json", "r") as f:
        event = json.load(f)
    return event

def test_botname_required():
    lb = bot()
    assert lb.botname == 'testbot'

def test_handle_resp_false():
    lb = bot()
    resp = dummy_response('{"ok": false}')
    assert lb._handle_resp(resp) == False

def test_handle_resp_true():
    lb = bot()
    resp = dummy_response('{"ok": true}')
    assert lb._handle_resp(resp) == True

def test_is_bot_msg_true():
    lb = bot()
    with open("tests/test_bot_message.json", "r") as f:
        data = json.load(f)
        data['token'] = 'test_token'
    lb.process_event(data)
    assert lb.is_bot_msg() == True

def test_is_bot_msg_false():
    lb = bot()
    with open("tests/test_user_event.json", "r") as f:
        data = json.load(f)
        data['token'] = 'test_token'
    lb.process_event(data)
    assert lb.is_bot_msg() == False

def test_verify_msg_false():
    lb = bot()
    lb.verification_token = 'bad_token'
    event = user_event()
    lb.process_event(event)
    assert lb.verify_msg() == False

def test_verify_msg_true():
    lb = bot()
    lb.verification_token = 'good_token'
    event = user_event()
    event['token'] = 'good_token'
    lb.process_event(event)
    assert lb.verify_msg() == True


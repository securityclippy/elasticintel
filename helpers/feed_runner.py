from helpers.lambdarunner import LambdaRunner

class FeedRunner(object):
    def __init__(self):
        self.lr = LambdaRunner(region="us-east-1")

    def invoke_feed_by_name(self, feed_name):
        event = {"schedule_feed": feed_name}
        result = self.lr.run_lambda("feed_scheduler_lambda_terraform", event=event)
        print(result)

#!/usr/bin/env python3


import os
import subprocess
import logging
import boto3
import json
import argparse
import zipfile
import json
from concurrent.futures import ThreadPoolExecutor
import shutil

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger()

class TerraformHelper(object):
    def __init__(self, environment=None):
        if environment is None:
            environment = 'dev'
        self.environment = environment
        self.project_root = os.path.abspath(os.path.curdir)
        self.config_file = os.path.join(self.project_root, "{}.conf".format(self.environment))
        if self.environment == 'dev':
            self.terraform_root = os.path.join(self.project_root, 'terraform', 'dev')
        else:
            self.terraform_root = os.path.join(self.project_root, 'terraform', 'prod')

    def init_teraform(self, working_dir):
        LOGGER.info(subprocess.check_call(["terraform", "init"]))
        if not ".terraform" in os.listdir(working_dir):
            LOGGER.warning("no .terraform dir found.  Initializing...")
            LOGGER.warning(os.listdir(working_dir))
            LOGGER.info(subprocess.check_call(["terraform", "init"]))
            return True
        if not "plugins" in os.listdir(os.path.join(working_dir, ".terraform")):
            LOGGER.warning("No plugins dir found, initializing...")
            LOGGER.warning(os.listdir(os.path.join(working_dir, ".terraform")))
            LOGGER.info(subprocess.check_call(["terraform", "init"]))
            return True
        return False

    def write_backend(self, filename, backend_bucket_name, profile_name, indent="    "):
        replacement_file = ""
        with open(filename, "r") as infile:
            for line in infile.readlines():
                if line.startswith("{}bucket".format(indent)):
                    replacement_file += '{}bucket = "{}"\n'.format(indent, backend_bucket_name)
                elif line.startswith("{}profile".format(indent)):
                    replacement_file += '{}profile = "{}"\n'.format(indent, profile_name)
                else:
                    replacement_file += line
        with open(filename, "w") as outfile:
            outfile.write(replacement_file)

    def init_backends(self, env):
        with open("{}.conf".format(env), "r") as infile:
            config = json.load(infile)
        bucket = config['backend_bucket_name']
        profile = config['aws_profile']
        for dir_name, sub_dir_list, file_list in os.walk(os.path.join(self.project_root, "terraform", env)):
            for filename in file_list:
                if filename == "backend.tf":
                    self.write_backend(filename="{}/{}".format(dir_name, filename), backend_bucket_name=bucket, profile_name=profile)
        ##modify initial backend
        fn = os.path.join(self.project_root, "terraform", env, "backend", "main.tf")
        self.write_backend(filename=fn, backend_bucket_name=bucket, profile_name=profile, indent="  ")

    def up_backend(self):
        LOGGER.name = "backend"
        os.chdir(self.project_root)
        backend_dir = os.path.join(self.terraform_root, "backend")
        os.chdir(backend_dir)
        self.init_teraform(backend_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))
        return

    def up_elasticsearch(self, plan=False):
        LOGGER.name = "elasticsearch"
        os.chdir(self.project_root)
        es_dir = os.path.join(self.terraform_root, "elasticsearch")
        print(es_dir)
        os.chdir(es_dir)
        LOGGER.info(os.path.abspath(os.curdir))
        self.init_teraform(es_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        if plan:
            LOGGER.info(subprocess.check_call(["terraform", "plan", "-var-file={}".format(self.config_file)]))
            return
        LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))
        return

    def up_lambda(self, plan=False):
        '''
        depends elasticsearch, s3, sns
        :param plan:
        :return:
        '''
        def zip_fs_lambda():
            os.chdir(self.project_root)
            relroot = os.path.join(self.project_root, "feed_scheduler_lambda")
            feed_lambda_path = os.path.join(self.terraform_root, "lambda/feed_scheduler_lambda")
            with zipfile.ZipFile(os.path.join(self.terraform_root, "lambda/feed_scheduler_lambda.zip"), "w", zipfile.ZIP_DEFLATED) as zip:
                for root, dirs, files in os.walk(relroot):
                    # add directory (needed for empty dirs)
                    zip.write(root, os.path.relpath(root, relroot))
                    for file in files:
                        filename = os.path.join(root, file)
                        if os.path.isfile(filename):  # regular files only
                            arcname = os.path.join(os.path.relpath(root, relroot), file)
                            zip.write(filename, arcname)
        def zip_if_lambda():
            os.chdir(self.project_root)
            relroot = os.path.join(self.project_root, "ingest_feed_lambda")
            ingest_lambda_path = os.path.join(self.terraform_root, "lambda/ingest_feed_lambda")
            with zipfile.ZipFile(os.path.join(self.terraform_root, "lambda/ingest_feed_lambda.zip"), "w", zipfile.ZIP_DEFLATED) as zip:
                for root, dirs, files in os.walk(relroot):
                    # add directory (needed for empty dirs)
                    zip.write(root, os.path.relpath(root, relroot))
                    for file in files:
                        filename = os.path.join(root, file)
                        if os.path.isfile(filename):  # regular files only
                            arcname = os.path.join(os.path.relpath(root, relroot), file)
                            zip.write(filename, arcname)
        LOGGER.name = "lambda"
        lambda_dir = os.path.join(self.terraform_root, "lambda")
        LOGGER.warning("terraform root: {}".format(self.terraform_root))
        LOGGER.info("zipping Feed Scheduler lambda...")
        #zip_fs_lambda()
        LOGGER.info("zipping Ingest Feed lambda...")
        #zip_if_lambda()
        os.chdir(lambda_dir)
        LOGGER.warning("calling terraform from: {}".format(lambda_dir))
        self.init_teraform(lambda_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        if plan:
            LOGGER.info(subprocess.check_call(["terraform", "plan", "-var-file={}".format(self.config_file)]))
            return
        LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))
        return

    def up_s3(self, plan=False):
        '''
        depends: Elasticsearch
        :param plan:
        :return:
        '''
        LOGGER.name = "s3"
        s3_dir = os.path.join(self.terraform_root, "s3")
        os.chdir(s3_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        self.init_teraform(s3_dir)
        if plan:
            LOGGER.info(subprocess.check_call(["terraform", "plan", "-var-file={}".format(self.config_file)]))
            return
        LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))
        return

    def up_sns(self, plan=False):
        '''
        depends elasticsearch, s3
        :param plan:
        :return:
        '''
        LOGGER.name = "sns"
        sns_dir = os.path.join(self.terraform_root, "sns")
        os.chdir(sns_dir)
        self.init_teraform(sns_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        if plan:
            LOGGER.info(subprocess.check_call(["terraform", "plan", "-var-file={}".format(self.config_file)]))
            return
        LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))
        return

    def up_intel_bot(self):
        '''
        turn up all components of intelbot
        :return:
        '''
        os.chdir(self.project_root)
        LOGGER.name = "IntelBot"
        ## setup ssm
        ssm_dir = os.path.join(self.terraform_root, "intelbot_ssm_parameter_store")
        os.chdir(ssm_dir)
        self.init_teraform(ssm_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))
        ## setup lambda
        os.chdir(self.project_root)
        lambda_dir = os.path.join(self.terraform_root, "intelbot_lambda")
        self.init_teraform(lambda_dir)
        os.chdir(lambda_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))

        ## setup api_gateway
        os.chdir(self.project_root)
        api_gateway_dir = os.path.join(self.terraform_root, "intelbot_api_gateway")
        self.init_teraform(api_gateway_dir)
        os.chdir(api_gateway_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))
        return


    def make_whois_lambda_dirs(self, region, force=False):
        if not force:
            if not os.path.exists(region):
                LOGGER.info("creating region dir: {}".format(region))
                os.mkdir(region)
            if not os.path.exists(os.path.join(region, "main.tf")):
                LOGGER.info("copying main.tf for: {}".format(region))
                shutil.copy("main.tf", os.path.join(region, "main.tf"))
            if not os.path.exists(os.path.join(region, "variables.tf")):
                LOGGER.info("copying variables.tf for: {}".format(region))
                shutil.copy("variables.tf", os.path.join(region, "variables.tf"))
            if not os.path.exists(os.path.join(region, "backend.tf")):
                LOGGER.info("copying backend for: {}".format(region))
                shutil.copy("backend.tf", os.path.join(region, "backend.tf"))
            return
        os.mkdir(region)
        shutil.copy("main.tf", os.path.join(region, "main.tf"))
        shutil.copy("variables.tf", os.path.join(region, "variables.tf"))
        shutil.copy("backend.tf", os.path.join(region, "backend.tf"))
        return

    def init_whois_lambda(self, region, parent_dir, profile):
        region_dir  = os.path.join(parent_dir, region)
        os.chdir(region_dir)
        with open(self.config_file, "r") as infile:
            config = json.load(infile)
        LOGGER.info(subprocess.check_call(["terraform",
                                           "init",
                                           #"-var", "profile={}".format(profile),
                                           #"-var","region={}".format(region),
                                           #"-auto-approve",
                                           '-var-file={}'.format(self.config_file),
                                           '-backend-config=bucket={}'.format(config['backend_bucket_name']),
                                           '-backend-config=profile={}'.format(profile),
                                           '-backend-config=key={}/whois_lambda/{}/terraform.tfstate'.format(self.environment, region),
                                           '-backend-config=region={}'.format("us-east-1"),
                                           '-backend-config=encrypt=true'
                                           ]))
        os.chdir(parent_dir)

    def up_whois_lambda(self):
        LOGGER.name = "whois_lambda"
        whois_dir = os.path.join(self.terraform_root, "whois_lambda")
        os.chdir(whois_dir)
        #self.init_teraform(whois_dir)
        region_list = ["us-east-1", "us-east-2", "us-west-1", "us-west-2",
                       "ca-central-1", "eu-central-1", "eu-west-1", "eu-west-2",
                        "ap-northeast-1", "ap-northeast-2", "ap-southeast-1",
                       "ap-southeast-2", "ap-south-1", "sa-east-1"]
        with open(os.path.join(self.project_root,
                               "{}.conf".format(self.environment)), "r") as infile:
            data = json.load(infile)
        profile = data['aws_profile']
        #with ThreadPoolExecutor(max_workers=5) as executor:
        for region in region_list:
            LOGGER.info(whois_dir)
            self.make_whois_lambda_dirs(region)
            self.init_whois_lambda(region, whois_dir, profile)
            os.chdir(region)
            LOGGER.info(subprocess.check_call(["terraform", "apply", "-var-file={}".format(self.config_file), "-auto-approve"]))
            os.chdir(whois_dir)
            #result = executor.submit(subprocess.check_call, "terraform",
                #LOGGER.info(result)
            #LOGGER.info(subprocess.check_call(["terraform", "apply", "-var"]))

    def up_feeds(self):
        os.chdir(self.project_root)
        #root_dir = os.path.abspath(root_dir)
        LOGGER.name = "FEEDS"
        s3 = boto3.resource("s3")
        feeds_dir = os.path.join(self.project_root, "feeds.d")
        feed_root = "feeds.d"
        print(feeds_dir)
        s3_dir = os.path.join(self.terraform_root, "s3")
        with open(self.config_file, "r") as infile:
            config = json.load(infile)
        bucket_name = config['s3_bucket_name']
        LOGGER.info(bucket_name)
        bucket = s3.Bucket(bucket_name)
        feeds = [i for i in os.listdir(feeds_dir) if i.endswith("json")]
        LOGGER.info("uploading: {}".format(feeds))
        # try:
        # bucket.Object("test_feeds.d/").load()
        # except Exception as e:
        # bucket.put_object("test_feeds.d/")
        for feed in feeds:
            feed = os.path.join(feed_root, feed)
            feed_file = os.path.abspath(feed)
            # path = os.path.join("test_feeds.d", feed)
            LOGGER.info(bucket.upload_file(feed_file, feed))

    def down_elasticsearch(self):
        LOGGER.name = "elasticsearch"
        os.chdir(self.project_root)
        es_dir = os.path.join(self.terraform_root, "elasticsearch")
        os.chdir(es_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        LOGGER.info(subprocess.check_call(["terraform", "destroy", "-var-file={}".format(self.config_file), "-force"]))
        return

    def down_lambda(self, plan=False):
        '''
        depends elasticsearch, s3, sns
        :param plan:
        :return:
        '''
        LOGGER.name = "lambda"
        lambda_dir = os.path.join(self.terraform_root, "lambda")
        os.chdir(lambda_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        LOGGER.info(subprocess.check_call(["terraform", "destroy", "-var-file={}".format(self.config_file), "-force"]))
        return

    def down_s3(self, bucket_name):
        '''
        depends: Elasticsearch
        :param plan:
        :return:
        '''
        LOGGER.name = "s3"
        s3_dir = os.path.join(self.terraform_root, "s3")
        os.chdir(s3_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        LOGGER.info(subprocess.check_call(["terraform", "destroy", "-var-file={}".format(self.config_file), "-force"]))
        return

    def down_sns(self):
        '''
        depends elasticsearch, s3
        :param plan:
        :return:
        '''
        LOGGER.name = "sns"
        sns_dir = os.path.join(self.terraform_root, "sns")
        os.chdir(sns_dir)
        LOGGER.info(subprocess.check_call(["terraform", "get"]))
        LOGGER.info(subprocess.check_call(["terraform", "destroy", "-var-file={}".format(self.config_file), "-force"]))
        return

    def down_whois_lambda(self):
        LOGGER.name = "whois_lambda"
        whois_dir = os.path.join(self.terraform_root, "whois_lambda")
        os.chdir(whois_dir)
        self.init_teraform(whois_dir)
        region_list = ["us-east-1", "us-east-2", "us-west-1", "us-west-2",
                       "ca-central-1", "eu-central-1", "eu-west-1", "eu-west-2",
                        "ap-northeast-1", "ap-northeast-2", "ap-southeast-1",
                       "ap-southeast-2", "ap-south-1", "sa-east-1"]
        with open(os.path.join(self.project_root,
                               "{}.conf".format(self.environment)), "r") as infile:
            data = json.load(infile)
        profile = data['aws_profile']
        with ThreadPoolExecutor(max_workers=5) as executor:
            for region in region_list:
                #LOGGER.info(subprocess.check_call(["terraform",
                                                   #"destroy", "-force", "-var", "profile={}".format(profile),
                                                   #"-var","region={}".format(region)]))
                executor.submit(subprocess.check_call, ["terraform",
                                                   "destroy", "-force", "-var", "profile={}".format(profile),
                                                   "-var","region={}".format(region)], )

